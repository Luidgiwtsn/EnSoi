"""Point d'entrée FastAPI — EnSoi."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlmodel import Session, text

from app.config import settings
from app.database import create_db_and_tables, engine
from app.routers.auth import router as auth_router
from app.routers.profils import router as profils_router, public_router
from app.routers.users import router as users_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ensoi")

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Démarrage EnSoi — env: {settings.environment}")
    if not settings.is_production():
        create_db_and_tables()
    yield
    logger.info("Arrêt EnSoi")


app = FastAPI(
    title="EnSoi API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production() else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_response_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    ms = (time.time() - start) * 1000
    if ms > 5000:
        logger.warning(f"Requête lente : {request.url.path} — {ms:.0f}ms")
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"
    return response


# Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profils_router, prefix="/api")
app.include_router(public_router)


@app.get("/api/health", tags=["Système"])
async def health():
    """Vérification état de l'API et de ses dépendances."""
    db_status = "ok"
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Échec healthcheck BDD : {e}")
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": "1.0.0",
        "database": db_status,
        "groq": "ok" if settings.groq_api_key else "missing",
    }
