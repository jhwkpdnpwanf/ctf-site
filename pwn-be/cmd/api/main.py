import os
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import uvicorn
from internal.config import get_settings
from internal.auth.jwt import create_access_token, require_user
from internal.db import init_engine, get_async_session
from internal.models import Base, User, Challenge, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt

import os
from dotenv import load_dotenv

def _load_env_flex():
    p = os.getenv("ENV_FILE")
    if p and os.path.exists(p):
        load_dotenv(p)
        return
    if os.path.exists(".env.local"):
        load_dotenv(".env.local")
        return
    if os.path.exists(".env"):
        load_dotenv(".env")

_load_env_flex()

app = FastAPI(title='pwnable API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['*'], allow_methods=['*'])

class SignupIn(BaseModel):
    email: str
    password: str

class SigninIn(BaseModel):
    email: str
    password: str

class ChallengeIn(BaseModel):
    slug: str
    title: str
    image: str
    mode: str
    port: int | None = None

class SessionCreateIn(BaseModel):
    challenge_id: int

class SessionOut(BaseModel):
    id: int
    ws_url: str

@app.on_event('startup')
async def on_startup():
    await init_engine()
    async with get_async_session() as s:
        async with s.begin():
            await s.run_sync(Base.metadata.create_all)

@app.post('/auth/signup')
async def signup(payload: SignupIn, session: AsyncSession = Depends(get_async_session)):
    q = await session.execute(select(User).where(User.email == payload.email))
    if q.scalar_one_or_none():
        raise HTTPException(400, 'email exists')
    u = User(email=payload.email, password_hash=bcrypt.hash(payload.password))
    session.add(u)
    await session.commit()
    token = create_access_token({'sub': str(u.id)})
    return {'access_token': token, 'token_type': 'bearer'}

@app.post('/auth/signin')
async def signin(payload: SigninIn, session: AsyncSession = Depends(get_async_session)):
    q = await session.execute(select(User).where(User.email == payload.email))
    u = q.scalar_one_or_none()
    if not u or not bcrypt.verify(payload.password, u.password_hash):
        raise HTTPException(401, 'invalid credentials')
    token = create_access_token({'sub': str(u.id)})
    return {'access_token': token, 'token_type': 'bearer'}

@app.get('/challenges')
async def list_challenges(session: AsyncSession = Depends(get_async_session)):
    q = await session.execute(select(Challenge).where(Challenge.is_public == True))
    items = q.scalars().all()
    return [{'id': c.id, 'slug': c.slug, 'title': c.title, 'mode': c.mode} for c in items]

@app.post('/challenges')
async def create_challenge(c: ChallengeIn, _: dict = Depends(require_user), session: AsyncSession = Depends(get_async_session)):
    ch = Challenge(slug=c.slug, title=c.title, image=c.image, mode=c.mode, port=c.port, is_public=True)
    session.add(ch)
    await session.commit()
    return {'id': ch.id}

@app.post('/sessions', response_model=SessionOut)
async def create_session(req: SessionCreateIn, user: dict = Depends(require_user), session: AsyncSession = Depends(get_async_session)):
    ch = await session.get(Challenge, req.challenge_id)
    if not ch or not ch.is_public:
        raise HTTPException(404, 'challenge not found')

    settings = get_settings()
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(f"{settings.RUNNER_URL}/start", json={'image': ch.image, 'mode': ch.mode, 'port': ch.port})
        if r.status_code != 200:
            raise HTTPException(502, 'runner failed')
        data = r.json()

    s = Session(user_id=int(user['sub']), challenge_id=ch.id, container_id=data['container_id'])
    session.add(s)
    await session.commit()

    ws_host = os.getenv('WS_PUBLIC_HOST')
    ws_port = os.getenv('WS_PUBLIC_PORT')
    ws_path = os.getenv('WS_PUBLIC_PATH', '/ws')
    if not ws_host or not ws_port:
        raise RuntimeError('WS_PUBLIC_HOST/PORT must be set')
    scheme = 'wss' if ws_port == '443' else 'ws'
    port_part = '' if ws_port in ('443', '80') else f':{ws_port}'
    ws_url = f"{scheme}://{ws_host}{port_part}{ws_path}/session/{s.id}"

    return SessionOut(id=s.id, ws_url=ws_url)

if __name__ == '__main__':
    uvicorn.run(app, host=os.getenv('API_HOST', '0.0.0.0'), port=int(os.getenv('API_PORT', '8080')))