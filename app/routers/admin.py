from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, Optional
import logging

from app.dependencies.auth import get_current_user
from app.services.event_store import get_event_store

router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger("uvicorn.error")

# Get event store instance
event_store = get_event_store()


@router.get("/events")
async def list_events(
    provider: Optional[str] = Query(default=None, description="Filter by provider (stripe, polar)"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of events to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    List webhook events with pagination and optional provider filter.
    
    Protected endpoint requiring Clerk authentication. Returns paginated list
    of webhook events stored in the event store.
    
    Args:
        provider: Optional filter by provider (stripe, polar)
        limit: Maximum number of events to return (1-1000)
        offset: Offset for pagination
        user: Authenticated user from dependency
        
    Returns:
        Dictionary containing events list and pagination metadata
    """
    logger.info("admin.list_events", extra={"user_id": user.get("user_id"), "provider": provider})
    
    try:
        result = await event_store.list_events(provider=provider, limit=limit, offset=offset)
        return {
            "ok": True,
            **result,
        }
    except Exception as e:
        logger.exception("admin.list_events_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events",
        )


@router.get("/events/{event_id}")
async def get_event(
    event_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get specific webhook event by ID.
    
    Protected endpoint requiring Clerk authentication. Returns detailed
    information about a specific webhook event.
    
    Args:
        event_id: Unique identifier of the event
        user: Authenticated user from dependency
        
    Returns:
        Dictionary containing event details
        
    Raises:
        HTTPException: 404 if event not found
    """
    logger.info("admin.get_event", extra={"user_id": user.get("user_id"), "event_id": event_id})
    
    try:
        event = await event_store.get_event(event_id)
        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event {event_id} not found",
            )
        return {
            "ok": True,
            "event": event,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("admin.get_event_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve event",
        )


@router.get("/stats")
async def get_stats(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get webhook statistics.
    
    Protected endpoint requiring Clerk authentication. Returns aggregate
    statistics about webhook events including counts by provider and status.
    
    Args:
        user: Authenticated user from dependency
        
    Returns:
        Dictionary containing statistics
    """
    logger.info("admin.get_stats", extra={"user_id": user.get("user_id")})
    
    try:
        stats = await event_store.get_stats()
        return {
            "ok": True,
            **stats,
        }
    except Exception as e:
        logger.exception("admin.get_stats_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics",
        )

