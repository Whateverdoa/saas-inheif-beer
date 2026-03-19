import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import webhooks, auth, admin, legal, invoices, compliance, orders, organizations, ogos_config, credits, beer

logger = logging.getLogger("uvicorn.error")

# On Vercel serverless, we skip the lifespan events as they don't work well
# Database initialization happens lazily on first request
IS_VERCEL = bool(os.getenv("VERCEL"))

app = FastAPI(title="OGOS SaaS API")

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
