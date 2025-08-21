from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from internal.config import get_settings

_engine = None
_session = None

async def init_engine():
    global _engine, _session
    dsn = get_settings().POSTGRES_DSN
    _engine = create_async_engine(dsn, echo=False, future=True)
    _session = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncSession:
    return _session()