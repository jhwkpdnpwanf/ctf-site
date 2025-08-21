import os, anyio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import docker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from internal.db import init_engine, get_async_session
from internal.models import Session as DbSession

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

app = FastAPI(title='ws-gateway')
client = docker.from_env()

@app.on_event('startup')
async def on_startup():
    await init_engine()

@app.websocket('/ws/session/{session_id}')
async def ws_pty(ws: WebSocket, session_id: int):
    await ws.accept()
    try:
        container_id = await resolve_container_id(session_id)
        sock = client.api.attach_socket(container_id, params={'stdin': 1, 'stdout': 1, 'stderr': 1, 'stream': 1})
        sock._sock.setblocking(False)

        async def ws_to_container():
            while True:
                data = await ws.receive_bytes()
                await anyio.to_thread.run_sync(sock._sock.send, data)

        async def container_to_ws():
            while True:
                chunk = await anyio.to_thread.run_sync(sock._sock.recv, 8192)
                if not chunk:
                    break
                await ws.send_bytes(chunk)

        async with anyio.create_task_group() as tg:
            tg.start_soon(ws_to_container)
            tg.start_soon(container_to_ws)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_text(f'error: {e}')
        except Exception:
            pass
    finally:
        try:
            await ws.close()
        except Exception:
            pass

async def resolve_container_id(session_id: int) -> str:
    async with get_async_session() as s:  # type: AsyncSession
        q = await s.execute(select(DbSession).where(DbSession.id == session_id))
        obj = q.scalar_one_or_none()
        if not obj:
            raise RuntimeError('session not found')
        return obj.container_id

if __name__ == '__main__':
    uvicorn.run(app, host=os.getenv('WS_HOST', '0.0.0.0'), port=int(os.getenv('WS_PORT', '8082')))