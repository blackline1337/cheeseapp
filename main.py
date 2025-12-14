from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import asyncpg, os, logging, sys, time

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=LOG_LEVEL,
    stream=sys.stdout,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

log = logging.getLogger("cheeseapp")


def build_dsn() -> str | None:
    keys = ("DATABASE_HOST", "DATABASE_PORT", "DATABASE_NAME", "DATABASE_USER", "DATABASE_PASSWORD")
    if not all(os.getenv(k) for k in keys):
        log.warning("db_config_missing")
        return None
    return (
        f"postgresql://{os.getenv('DATABASE_USER')}:"
        f"{os.getenv('DATABASE_PASSWORD')}@"
        f"{os.getenv('DATABASE_HOST')}:"
        f"{os.getenv('DATABASE_PORT')}/"
        f"{os.getenv('DATABASE_NAME')}"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = None
    try:
        if dsn := build_dsn():
            app.state.pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
            log.info("db_pool_ready")
    except Exception as e:
        log.error("db_init_failed", extra={"error": str(e)})
    yield
    if app.state.pool:
        await app.state.pool.close()
        log.info("db_pool_closed")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    log.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round((time.time() - start) * 1000, 2),
        },
    )
    return response


@app.get("/live")
def live():
    log.debug("live_check")
    return {"status": "alive"}


@app.get("/ready")
async def ready():
    try:
        async with app.state.pool.acquire() as c:
            await c.execute("SELECT 1")
        log.debug("ready_check_ok")
        return {"status": "ready"}
    except Exception as e:
        log.warning("ready_check_failed", extra={"error": str(e)})
        return {"status": "not_ready"}
