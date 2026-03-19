import os
import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import webhooks, auth, admin, legal, invoices, compliance, orders, organizations, ogos_config, credits, beer
from app.services.database import get_database

logger = logging.getLogger("uvicorn.error")

# Check if running on Vercel
IS_VERCEL = bool(os.getenv("VERCEL"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Initializing database...")
    db = get_database()
    if hasattr(db, "init_db"):
        await db.init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="OGOS SaaS API",
    lifespan=lifespan,
)

# CORS – adjust to your frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://saas-inheif-beer.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check at root
@app.get("/healthz")
async def healthz():
    return {"ok": True}


# On Vercel, routes come in as /api/beer/... so we mount at /api
# Locally, routes come in as /beer/... so we mount at root
api_prefix = "/api" if IS_VERCEL else ""

# Create a sub-router for all API routes
api_router = APIRouter(prefix=api_prefix)

# Include all routers in the API router
api_router.include_router(webhooks.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(legal.router)
api_router.include_router(invoices.router)
api_router.include_router(compliance.router)
api_router.include_router(orders.router)
api_router.include_router(organizations.router)
api_router.include_router(ogos_config.router)
api_router.include_router(credits.router)
api_router.include_router(beer.router)

# Mount the API router
app.include_router(api_router)
