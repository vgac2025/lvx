"""FastAPI application — ARTCB MVP Phase 2+3."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.deps import build_app_state
from api.routes import router as api_router
from api.websocket import router as ws_router
from artcb.logging_config import setup_logging

setup_logging("artcb.api")
logger = logging.getLogger("artcb.api")


def create_app() -> FastAPI:
    app = FastAPI(title="ARTCB API", version="0.3.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.artcb = build_app_state()
    app.include_router(api_router)
    app.include_router(ws_router)
    logger.debug("ARTCB API started debug=%s", app.state.artcb.settings.debug)
    return app


app = create_app()
