import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import router
from app.api.websockets import manager
from app.core.db import create_db_and_tables
from app.services.ml_registry import load_model


# ── Application Lifespan ──────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup and load ML model."""
    create_db_and_tables()
    load_model()
    yield


# ── App Factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sentinel Logistics API",
    description="Delivery risk prediction & route intelligence platform powered by FastAPI + SQLModel.",
    version="2.1.0",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://myproject-xbsg-4wyzka7bo-botbender167s-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API Key Middleware ────────────────────────────────────────────────────────

SENTINEL_API_KEY = os.environ.get("SENTINEL_API_KEY", "sentinel-dev-key")

# Paths that bypass API key auth
AUTH_EXEMPT_PATHS = {
    "/api/health",
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/webhook/zomato",
    "/ws",               # <<< WebSocket path
    "/api/ws/feed",      # Legacy alias
}


@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """
    Validate the X-API-Key header on all protected routes.
    Exempt paths and WebSocket upgrades bypass auth.
    """
    path = request.url.path

    # Bypass auth for WS upgrades and exempt paths
    if path in AUTH_EXEMPT_PATHS or request.method == "OPTIONS":
        return await call_next(request)

    api_key = request.headers.get("X-API-Key", "")
    if api_key != SENTINEL_API_KEY:
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Unauthorized — invalid or missing X-API-Key header.",
                "hint": "Use X-API-Key: sentinel-dev-key for local development.",
            },
        )

    return await call_next(request)


# ── REST Routes ───────────────────────────────────────────────────────────────

app.include_router(router, prefix="/api")


# ── WebSocket Route ───────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep alive — client does not need to send anything
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS error: {e}")
        manager.disconnect(websocket)
