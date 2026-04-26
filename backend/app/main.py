"""
main.py
───────
FastAPI application factory.

Registered routers (all under /api/v1):
  /auth          – register, login, logout, refresh
  /users         – GET/PUT/DELETE /me
  /categories    – CRUD
  /expenses      – CRUD + filtering/pagination
  /budgets       – CRUD
  /dashboard     – GET /summary
  /insights      – GET + POST /regenerate (rate-limited)

Rate limiting (slowapi):
  - Applied globally via SlowAPIMiddleware
  - /insights/regenerate: 10 requests/hour per authenticated user
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.routers import (
    auth,
    budgets,
    categories,
    dashboard,
    expenses,
    insights,
    users,
)
from app.routers.insights import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ───────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Expense Tracker API starting up…")
    yield
    logger.info("AI Expense Tracker API shutting down…")


# ── App factory ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Expense Tracker",
    description=(
        "Personal finance tracker with AI-generated insights.\n\n"
        "All protected routes require `Authorization: Bearer <access_token>`."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── Rate limiter state (required by slowapi) ───────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# ── CORS ───────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handlers ──────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found"},
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # Let FastAPI's default handler format the body; we just add a top-level key
    from fastapi.exception_handlers import request_validation_exception_handler
    from fastapi.exceptions import RequestValidationError

    if isinstance(exc, RequestValidationError):
        return await request_validation_exception_handler(request, exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


# ── Router registration ────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth.router,       prefix=API_PREFIX)
app.include_router(users.router,      prefix=API_PREFIX)
app.include_router(categories.router, prefix=API_PREFIX)
app.include_router(expenses.router,   prefix=API_PREFIX)
app.include_router(budgets.router,    prefix=API_PREFIX)
app.include_router(dashboard.router,  prefix=API_PREFIX)
app.include_router(insights.router,   prefix=API_PREFIX)


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health", tags=["meta"], summary="Health check")
async def health() -> dict:
    return {"status": "ok", "version": "1.0.0"}
