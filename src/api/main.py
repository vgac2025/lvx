"""FastAPI application — ARTCB MVP Phase 2+3."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from artcb.logging_config import setup_logging
from api.connectors_routes import router as connectors_router
from api.dashboard_routes import router as dashboard_router
from api.deps import build_app_state
from api.devnet_routes import router as devnet_router
from api.governance_routes import router as governance_router
from api.groups_routes import router as groups_router
from api.mining_routes import router as mining_router
from api.notifications_routes import router as notifications_router
from api.p2p_routes import router as p2p_router
from api.pool_routes import router as pool_router
from api.routes import router as api_router
from api.symbols_routes import router as symbols_router
from api.websocket import router as ws_router

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
    app.include_router(devnet_router)
    app.include_router(symbols_router)
    app.include_router(groups_router)
    app.include_router(connectors_router)
    app.include_router(mining_router)
    app.include_router(governance_router)
    app.include_router(p2p_router)
    app.include_router(pool_router)
    app.include_router(notifications_router)
    app.include_router(dashboard_router)
    app.include_router(ws_router)
    logger.debug("ARTCB API started debug=%s", app.state.artcb.settings.debug)
    return app


app = create_app()
