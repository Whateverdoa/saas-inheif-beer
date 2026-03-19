"""Legal document endpoints."""
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from typing import Optional
import logging

from app.services.compliance_service import get_compliance_service

router = APIRouter(prefix="/legal", tags=["legal"])
logger = logging.getLogger("uvicorn.error")

compliance_service = get_compliance_service()


@router.get("/terms")
async def get_terms_of_service(
    format: Optional[str] = Query(default="markdown", pattern="^(markdown|html)$")
):
    """Get Terms of Service document."""
    try:
        doc = compliance_service.get_legal_document("terms", format=format)
        if format == "html":
            return HTMLResponse(content=doc["content"])
        return PlainTextResponse(content=doc["content"], media_type="text/markdown")
    except Exception as e:
        logger.exception("legal.get_terms_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Terms of Service",
        )


@router.get("/privacy")
async def get_privacy_policy(
    format: Optional[str] = Query(default="markdown", pattern="^(markdown|html)$")
):
    """Get Privacy Policy document."""
    try:
        doc = compliance_service.get_legal_document("privacy", format=format)
        if format == "html":
            return HTMLResponse(content=doc["content"])
        return PlainTextResponse(content=doc["content"], media_type="text/markdown")
    except Exception as e:
        logger.exception("legal.get_privacy_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Privacy Policy",
        )


@router.get("/dpa")
async def get_dpa(
    format: Optional[str] = Query(default="markdown", pattern="^(markdown|html)$")
):
    """Get Data Processing Agreement (DPA/AVG) document."""
    try:
        doc = compliance_service.get_legal_document("dpa", format=format)
        if format == "html":
            return HTMLResponse(content=doc["content"])
        return PlainTextResponse(content=doc["content"], media_type="text/markdown")
    except Exception as e:
        logger.exception("legal.get_dpa_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Data Processing Agreement",
        )


@router.get("/cookies")
async def get_cookie_policy(
    format: Optional[str] = Query(default="markdown", pattern="^(markdown|html)$")
):
    """Get Cookie Policy document."""
    try:
        doc = compliance_service.get_legal_document("cookies", format=format)
        if format == "html":
            return HTMLResponse(content=doc["content"])
        return PlainTextResponse(content=doc["content"], media_type="text/markdown")
    except Exception as e:
        logger.exception("legal.get_cookies_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Cookie Policy",
        )


@router.get("/documents")
async def list_legal_documents():
    """List all available legal documents."""
    try:
        documents = compliance_service.list_legal_documents()
        return {"ok": True, "documents": documents}
    except Exception as e:
        logger.exception("legal.list_documents_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list legal documents",
        )

