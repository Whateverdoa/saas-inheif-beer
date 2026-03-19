"""OGOS configuration endpoints for frontend."""
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging

from app.services.ogos_service import get_ogos_service

router = APIRouter(prefix="/ogos", tags=["ogos"])
logger = logging.getLogger("uvicorn.error")


@router.get("/locations", response_model=dict)
async def get_locations():
    """
    Get available OGOS locations.
    Public endpoint for frontend configuration.
    """
    try:
        ogos_service = get_ogos_service()
        locations = await ogos_service.get_locations()
        return {
            "ok": True,
            "locations": [loc.dict() for loc in locations],
        }
    except Exception as e:
        logger.exception("ogos.locations_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get locations")


@router.get("/materials", response_model=dict)
async def get_materials(
    location_code: str = Query(..., description="Location code"),
):
    """
    Get available materials for location.
    """
    try:
        ogos_service = get_ogos_service()
        materials = await ogos_service.get_materials(location_code)
        return {
            "ok": True,
            "materials": [mat.dict() for mat in materials],
        }
    except Exception as e:
        logger.exception("ogos.materials_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get materials")


@router.get("/shapes", response_model=dict)
async def get_shapes(
    location_code: str = Query(..., description="Location code"),
):
    """
    Get available shapes for location.
    """
    try:
        ogos_service = get_ogos_service()
        shapes = await ogos_service.get_shapes(location_code)
        return {
            "ok": True,
            "shapes": shapes,
        }
    except Exception as e:
        logger.exception("ogos.shapes_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get shapes")


@router.get("/adhesives", response_model=dict)
async def get_adhesives(
    location_code: str = Query(..., description="Location code"),
):
    """
    Get available adhesives for location.
    """
    try:
        ogos_service = get_ogos_service()
        adhesives = await ogos_service.get_adhesives(location_code)
        return {
            "ok": True,
            "adhesives": adhesives,
        }
    except Exception as e:
        logger.exception("ogos.adhesives_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get adhesives")


@router.get("/shipping-methods", response_model=dict)
async def get_shipping_methods(
    location_code: str = Query(..., description="Location code"),
):
    """
    Get available shipping methods for location.
    """
    try:
        ogos_service = get_ogos_service()
        shipping_methods = await ogos_service.get_shipping_methods(location_code)
        return {
            "ok": True,
            "shipping_methods": shipping_methods,
        }
    except Exception as e:
        logger.exception("ogos.shipping_methods_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get shipping methods")

