import os
import asyncpg
from fastapi import FastAPI

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
pool: asyncpg.Pool | None = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=5,
        timeout=2
    )

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

@app.get("/live")
def live():
    return {"status": "alive"}

@app.get("/ready")
async def ready():
    if pool is None:
        return {"status": "not_ready"}

    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}
