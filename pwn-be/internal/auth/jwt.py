import os, time, jwt
from fastapi import HTTPException, Header

SECRET = os.getenv("JWT_SECRET", "change-me")

def create_access_token(claims: dict, ttl: int = 3600) -> str:
    payload = {**claims, "exp": int(time.time()) + ttl}
    return jwt.encode(payload, SECRET, algorithm="HS256")

def require_user(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing bearer")
    token = authorization.split(" ", 1)[1]
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "invalid token")