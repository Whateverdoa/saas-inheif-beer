import os
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


# Include all routers
app.include_router(webhooks.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(legal.router)
app.include_router(invoices.router)
app.include_router(compliance.router)
app.include_router(orders.router)
app.include_router(organizations.router)
app.include_router(ogos_config.router)
app.include_router(credits.router)
app.include_router(beer.router)
