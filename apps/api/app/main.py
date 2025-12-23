from time import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging, logger

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title=settings.project_name, version=settings.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time()
    response = await call_next(request)
    duration_ms = (time() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f} ms)"
    )
    return response


@app.get("/", include_in_schema=False)
def read_root() -> dict[str, str]:
    return {"status": "ok", "message": "API is running"}
