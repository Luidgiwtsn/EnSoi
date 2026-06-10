"""Point d'entrée FastAPI — EnSoi."""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import create_db_and_tables

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
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def response_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    ms = (time.time() - start) * 1000
    if ms > 5000:
        logger.warning(f"Requête lente : {request.url.path} — {ms:.0f}ms")
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"
    return response


# Routers — décommentés au fur et à mesure
# from app.routers import auth, profils, users
# app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# app.include_router(profils.router, prefix="/api", tags=["Profils"])
# app.include_router(users.router, prefix="/users", tags=["Users"])


@app.get("/api/health", tags=["Système"])
async def health():
    """Vérification état de l'API."""
    from sqlmodel import Session, text
    try:
        with Session(__import__('app.database', fromlist=['engine']).engine) as s:
            s.exec(text("SELECT 1"))
        db = "ok"
    except Exception:
        db = "error"

    return {
        "status": "ok" if db == "ok" else "degraded",
        "version": "1.0.0",
        "database": db,
        "groq": "ok" if settings.groq_api_key else "missing",
    }
