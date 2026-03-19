"""Organization management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging

from app.dependencies.auth import get_current_user
from app.models import Organization, OrgSubscriptionStatus
from app.services.database import get_database
from app.services.subscription_service import get_subscription_service

router = APIRouter(prefix="/organizations", tags=["organizations"])
logger = logging.getLogger("uvicorn.error")


@router.post("", response_model=dict)
async def create_organization(
    name: str,
    kvk_number: Optional[str] = None,
    address: Optional[str] = None,
    contact_email: Optional[str] = None,
    ogos_guid: str = "",
    rate_limit_per_day: int = 100,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new organization (B2B).
    """
    try:
        if not ogos_guid:
            raise ValueError("OGOS GUID is required")
        
        db = get_database()
        
        org = Organization(
            user_id=current_user["user_id"],
            name=name,
            kvk_number=kvk_number,
            address=address,
            contact_email=contact_email,
            ogos_guid=ogos_guid,
            rate_limit_per_day=rate_limit_per_day,
        )
        
        org = await db.create_organization(org)
        
        return {"ok": True, "organization": org.dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("organization.create_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create organization")


@router.get("", response_model=dict)
async def list_organizations(
    current_user: dict = Depends(get_current_user),
):
    """
    List organizations for current user.
    """
    try:
        db = get_database()
        orgs = await db.get_organizations_by_user(current_user["user_id"])
        return {
            "ok": True,
            "organizations": [org.dict() for org in orgs],
        }
    
    except Exception as e:
        logger.exception("organization.list_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list organizations")


@router.get("/{org_id}", response_model=dict)
async def get_organization(
    org_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get organization details.
    """
    try:
        db = get_database()
        org = await db.get_organization(org_id)
        
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        
        if org.user_id != current_user["user_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        return {"ok": True, "organization": org.dict()}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("organization.get_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get organization")


@router.put("/{org_id}", response_model=dict)
async def update_organization(
    org_id: str,
    name: Optional[str] = None,
    kvk_number: Optional[str] = None,
    address: Optional[str] = None,
    contact_email: Optional[str] = None,
    ogos_guid: Optional[str] = None,
    rate_limit_per_day: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    Update organization.
    """
    try:
        db = get_database()
        org = await db.get_organization(org_id)
        
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        
        if org.user_id != current_user["user_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        updates = {}
        if name is not None:
            updates["name"] = name
        if kvk_number is not None:
            updates["kvk_number"] = kvk_number
        if address is not None:
            updates["address"] = address
        if contact_email is not None:
            updates["contact_email"] = contact_email
        if ogos_guid is not None:
            updates["ogos_guid"] = ogos_guid
        if rate_limit_per_day is not None:
            updates["rate_limit_per_day"] = rate_limit_per_day
        
        org = await db.update_organization(org_id, **updates)
        
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        
        return {"ok": True, "organization": org.dict()}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("organization.update_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update organization")


@router.get("/{org_id}/subscription", response_model=dict)
async def get_organization_subscription(
    org_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get subscription status for organization.
    """
    try:
        db = get_database()
        org = await db.get_organization(org_id)
        
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        
        if org.user_id != current_user["user_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        subscription_service = get_subscription_service()
        subscription = await subscription_service.get_organization_subscription(org_id)
        
        is_active = await subscription_service.validate_subscription_active(org_id)
        
        return {
            "ok": True,
            "subscription": subscription.dict() if subscription else None,
            "is_active": is_active,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("organization.subscription_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get subscription")

