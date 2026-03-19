"""Credit management endpoints for B2C."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from decimal import Decimal
import logging

from app.dependencies.auth import get_current_user
from app.services.credit_service import get_credit_service
from app.services.database import get_database

router = APIRouter(prefix="/credits", tags=["credits"])
logger = logging.getLogger("uvicorn.error")


@router.get("/balance", response_model=dict)
async def get_credit_balance(
    current_user: dict = Depends(get_current_user),
):
    """
    Get credit balance for current user.
    """
    try:
        credit_service = get_credit_service()
        balance = await credit_service.get_credit_balance(current_user["user_id"])
        return {
            "ok": True,
            "balance": float(balance),
        }
    except Exception as e:
        logger.exception("credits.balance_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get credit balance")


@router.post("/purchase", response_model=dict)
async def purchase_credits(
    amount: Decimal,
    current_user: dict = Depends(get_current_user),
):
    """
    Purchase credits (creates Stripe payment intent).
    
    Note: This endpoint should create a Stripe payment intent and return
    the client secret for frontend confirmation. Full implementation
    requires Stripe integration.
    """
    try:
        # TODO: Integrate with Stripe to create payment intent
        # For now, return a placeholder response
        return {
            "ok": True,
            "message": "Credit purchase initiated",
            "amount": float(amount),
            "note": "Stripe integration pending - use Stripe API to create payment intent",
        }
    except Exception as e:
        logger.exception("credits.purchase_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to purchase credits")


@router.get("/history", response_model=dict)
async def get_credit_history(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
):
    """
    Get credit transaction history.
    """
    try:
        db = get_database()
        # TODO: Implement credit history query in database adapter
        return {
            "ok": True,
            "transactions": [],
            "total": 0,
            "limit": limit,
            "offset": offset,
            "note": "Credit history query pending database implementation",
        }
    except Exception as e:
        logger.exception("credits.history_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get credit history")

