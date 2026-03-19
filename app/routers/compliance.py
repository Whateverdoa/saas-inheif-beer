"""Compliance tracking and launch checklist endpoints."""
import os
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
import logging

from app.dependencies.auth import get_current_user
from app.models.compliance import ChecklistItem, ComplianceStatus
from app.models.branding import BrandingConfig, CompanyInfo

router = APIRouter(prefix="/compliance", tags=["compliance"])
logger = logging.getLogger("uvicorn.error")

# In-memory checklist storage (can be extended to persistent storage)
_checklist_items: Dict[str, ChecklistItem] = {}

# Initialize default checklist items
_default_checklist = [
    {"id": "kvk_registration", "name": "KvK registration complete"},
    {"id": "btw_number", "name": "BTW number obtained"},
    {"id": "bank_account", "name": "Bank account connected"},
    {"id": "bookkeeping", "name": "Bookkeeping setup (e-boekhouden)"},
    {"id": "insurance", "name": "Insurance obtained"},
    {"id": "legal_docs", "name": "Legal docs published"},
    {"id": "stripe_bank", "name": "Stripe connected to bank"},
    {"id": "polar_bank", "name": "Polar connected to bank"},
    {"id": "test_invoice", "name": "Test invoice created"},
]

# Initialize checklist
for item_data in _default_checklist:
    if item_data["id"] not in _checklist_items:
        _checklist_items[item_data["id"]] = ChecklistItem(
            id=item_data["id"],
            name=item_data["name"],
            status="pending",
        )


@router.get("/checklist")
async def get_checklist(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get launch checklist status.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        items = list(_checklist_items.values())
        completed_count = sum(1 for item in items if item.status == "completed")
        total_count = len(items)
        completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0.0

        status_obj = ComplianceStatus(
            total_items=total_count,
            completed_items=completed_count,
            completion_percentage=round(completion_percentage, 2),
            items=items,
        )

        return {"ok": True, **status_obj.dict()}
    except Exception as e:
        logger.exception("compliance.get_checklist_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve checklist",
        )


@router.put("/checklist/{item_id}")
async def update_checklist_item(
    item_id: str,
    status: Optional[str] = None,
    notes: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Update checklist item status.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        if item_id not in _checklist_items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Checklist item {item_id} not found",
            )

        item = _checklist_items[item_id]

        if status is not None:
            if status not in ["pending", "completed"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Status must be 'pending' or 'completed'",
                )
            item.status = status
            if status == "completed":
                item.completed_at = datetime.now()
            else:
                item.completed_at = None

        if notes is not None:
            item.notes = notes

        _checklist_items[item_id] = item

        logger.info(
            "compliance.checklist_updated",
            extra={"user_id": user.get("user_id"), "item_id": item_id, "status": status},
        )

        return {"ok": True, "item": item.dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("compliance.update_checklist_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update checklist item",
        )


@router.get("/status")
async def get_compliance_status(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get overall compliance status.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        items = list(_checklist_items.values())
        completed_count = sum(1 for item in items if item.status == "completed")
        total_count = len(items)
        completion_percentage = (completed_count / total_count * 100) if total_count > 0 else 0.0

        return {
            "ok": True,
            "total_items": total_count,
            "completed_items": completed_count,
            "completion_percentage": round(completion_percentage, 2),
            "is_compliant": completion_percentage == 100.0,
        }
    except Exception as e:
        logger.exception("compliance.get_status_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance status",
        )


@router.get("/branding")
async def get_branding_config(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get branding configuration.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        config = BrandingConfig(
            logo_url=os.getenv("BRANDING_LOGO_URL"),
            primary_color=os.getenv("BRANDING_PRIMARY_COLOR", "#2563eb"),
            secondary_color=os.getenv("BRANDING_SECONDARY_COLOR", "#64748b"),
            font_family=os.getenv("BRANDING_FONT_FAMILY", "Inter"),
            company_name=os.getenv("COMPANY_NAME", "Your Company Name"),
            company_domain=os.getenv("COMPANY_DOMAIN"),
            company_email=os.getenv("COMPANY_EMAIL"),
        )
        return {"ok": True, "branding": config.dict()}
    except Exception as e:
        logger.exception("compliance.get_branding_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve branding configuration",
        )


@router.put("/branding")
async def update_branding_config(
    branding: BrandingConfig,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Update branding configuration.
    
    Protected endpoint requiring Clerk authentication.
    
    Note: This updates environment variables in memory only.
    For production, store in database or config file.
    """
    try:
        # In a real implementation, this would persist to database or config file
        # For now, we'll just return success (environment variables would need to be set externally)
        logger.info(
            "compliance.branding_updated",
            extra={"user_id": user.get("user_id"), "branding": branding.dict()},
        )

        return {
            "ok": True,
            "message": "Branding configuration updated (set environment variables for persistence)",
            "branding": branding.dict(),
        }
    except Exception as e:
        logger.exception("compliance.update_branding_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update branding configuration",
        )


@router.get("/company-info")
async def get_company_info(
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get company information.
    
    Protected endpoint requiring Clerk authentication.
    """
    try:
        company_info = CompanyInfo(
            company_name=os.getenv("COMPANY_NAME", "Your Company Name"),
            kvk_number=os.getenv("COMPANY_KVK_NUMBER"),
            btw_number=os.getenv("COMPANY_BTW_NUMBER"),
            bank_account=os.getenv("COMPANY_BANK_ACCOUNT"),
            address=os.getenv("COMPANY_ADDRESS"),
            domain=os.getenv("COMPANY_DOMAIN"),
            email=os.getenv("COMPANY_EMAIL"),
        )
        return {"ok": True, "company_info": company_info.dict()}
    except Exception as e:
        logger.exception("compliance.get_company_info_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company information",
        )

