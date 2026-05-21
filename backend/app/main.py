from contextlib import asynccontextmanager
from datetime import datetime
import logging
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.chroma import chroma_service
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.openapi_docs import OPENAPI_TAGS, install_chinese_openapi


logger = logging.getLogger(__name__)

DEFAULT_SECRET_KEY = "your-secret-key-change-in-production"
DEFAULT_ADMIN_PASSWORD = "admin123"


def _check_production_secrets() -> None:
    if settings.DEBUG:
        return
    if settings.SECRET_KEY == DEFAULT_SECRET_KEY:
        logger.warning(
            "SECRET_KEY uses the placeholder default; set SECRET_KEY in the environment for production."
        )
    if settings.ADMIN_INITIAL_PASSWORD == DEFAULT_ADMIN_PASSWORD:
        logger.warning(
            "ADMIN_INITIAL_PASSWORD uses the default 'admin123'; override it before deploying."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _check_production_secrets()
    create_db_and_tables()
    try:
        chroma_service.connect()
    except Exception as exc:
        logger.warning("Chroma connection failed: %s", exc)
    yield


app = FastAPI(
    title="行政智能体 API 文档",
    description="行政智能体后端接口文档，覆盖认证登录、用户、工单、任务、审批、资产、知识库、系统设置和智能助手。",
    version=settings.APP_VERSION,
    openapi_tags=OPENAPI_TAGS,
    lifespan=lifespan,
)

install_chinese_openapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/")
async def root():
    index_html = FRONTEND_DIST / "index.html"
    if index_html.exists():
        return FileResponse(index_html)
    return {
        "status": "ok",
        "message": "Admin Agent API is running",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {"api": "ok"},
    }


@app.get("/health/ready")
async def readiness_check():
    return {"status": "ready"}


@app.get("/health/live")
async def liveness_check():
    return {"status": "alive"}


@app.get("/metrics")
async def metrics():
    return Response(
        "process_cpu_usage 0\nprocess_memory_usage 0\n",
        media_type="text/plain",
    )


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    if full_path in {"favicon.svg", "icons.svg"}:
        asset = FRONTEND_DIST / full_path
        if asset.exists():
            return FileResponse(asset)

    index_html = FRONTEND_DIST / "index.html"
    if index_html.exists() and not full_path.startswith(("api/", "health", "metrics", "docs", "redoc", "openapi.json")):
        return FileResponse(index_html)

    return {
        "status": "ok",
        "message": "Admin Agent API is running",
        "version": settings.APP_VERSION,
    }
