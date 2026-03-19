"""Minimal test endpoint for Vercel."""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Minimal test endpoint"}

@app.get("/healthz")
async def healthz():
    return {"ok": True}

handler = app
