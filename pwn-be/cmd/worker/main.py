import os, asyncio
from dotenv import load_dotenv
import redis

load_dotenv()
r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

async def handle_job(payload: str):
    return

async def main():
    while True:
        item = r.blpop("jobs:queue", timeout=5)
        if not item:
            await asyncio.sleep(1)
            continue
        _, payload = item
        await handle_job(payload.decode())

if __name__ == "__main__":
    asyncio.run(main())