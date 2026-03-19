import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import webhooks, auth, admin, legal, invoices, compliance, orders, organizations, ogos_config, credits, beer
from app.services.database import get_database

logger = logging.getLogger("uvicorn.error")


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


app = FastAPI(title="OGOS SaaS API", lifespan=lifespan)

# CORS – adjust to your frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.example"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public webhook endpoints (protected by signature verification)
app.include_router(webhooks.router)

# Authentication endpoints
app.include_router(auth.router)

# Protected admin endpoints (require Clerk authentication)
app.include_router(admin.router)

# Legal document endpoints (public)
app.include_router(legal.router)

# Invoice endpoints (protected)
app.include_router(invoices.router)

# Compliance tracking endpoints (protected)
app.include_router(compliance.router)

# Order management endpoints (protected)
app.include_router(orders.router)

# Organization management endpoints (protected)
app.include_router(organizations.router)

# OGOS configuration endpoints (public)
app.include_router(ogos_config.router)

# Credit management endpoints (protected)
app.include_router(credits.router)

# Beer label endpoints (public configuration, protected orders)
app.include_router(beer.router)

@app.get("/healthz")
async def healthz():
    return {"ok": True}
