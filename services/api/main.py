"""Social Bot Hunter — FastAPI REST API Service."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware import SimpleRateLimiterMiddleware, TraceCorrelationMiddleware
from .routers import (
    accounts,
    adapters,
    audit,
    auth,
    capabilities,
    coordination,
    detection_ml,
    diff,
    health,
    imports,
    networks,
    runtime,
    scans,
    settings,
    storage_mgmt,
    users,
)
from .schemas import RootResponse

app = FastAPI(
    title="Social Bot Hunter API",
    description=(
        "Production-oriented investigation API for cross-platform bot-risk assessment "
        "and coordinated-network detection with transparent evidence, provenance, and role-based access control."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration for local development and dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares: rate limiting and trace correlation
app.add_middleware(SimpleRateLimiterMiddleware)
app.add_middleware(TraceCorrelationMiddleware)

# Mount versioned API routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(capabilities.router, prefix="/api/v1")
app.include_router(scans.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(networks.router, prefix="/api/v1")
app.include_router(coordination.router, prefix="/api/v1")
app.include_router(diff.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")
app.include_router(adapters.router, prefix="/api/v1")
app.include_router(detection_ml.router, prefix="/api/v1")
app.include_router(runtime.router, prefix="/api/v1")
app.include_router(storage_mgmt.router, prefix="/api/v1")


@app.get("/api/v1/openapi.json", include_in_schema=False)
def openapi_v1():
    return app.openapi()


@app.get("/", response_model=RootResponse)
def root():
    return RootResponse(
        service="Social Bot Hunter API",
        docs="/docs",
        health="/api/v1/health",
        version="0.1.0",
    )
