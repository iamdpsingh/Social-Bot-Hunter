"""Social Bot Hunter — FastAPI REST API Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import accounts, capabilities, health, imports, networks, scans

app = FastAPI(
    title="Social Bot Hunter API",
    description=(
        "Production-oriented investigation API for cross-platform bot-risk assessment "
        "and coordinated-network detection with transparent evidence and provenance."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS configuration for local development and dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount versioned API routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(capabilities.router, prefix="/api/v1")
app.include_router(scans.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(networks.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "service": "Social Bot Hunter API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "version": "0.1.0",
    }
