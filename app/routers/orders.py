"""Order management endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.dependencies.auth import get_current_user
from app.models import OrderType, OrderSpecifications, ShippingAddress
from app.services.order_service import get_order_service

router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger("uvicorn.error")


@router.post("", response_model=dict)
async def create_order(
    order_type: OrderType = Form(...),
    reference: str = Form(...),
    location_code: str = Form(...),
    material_code: Optional[str] = Form(None),
    quantity: int = Form(...),
    shape: Optional[str] = Form(None),
    adhesive: Optional[str] = Form(None),
    core_size: Optional[str] = Form(None),
    product_type: Optional[str] = Form(None),
    shipping_method: Optional[str] = Form(None),
    shipping_name: str = Form(...),
    shipping_street: str = Form(...),
    shipping_city: str = Form(...),
    shipping_postal_code: str = Form(...),
    shipping_country: str = Form(default="NL"),
    shipping_phone: Optional[str] = Form(None),
    org_id: Optional[str] = Form(None),
    pdf_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new order with PDF upload.
    
    For B2B orders, org_id is required.
    For B2C orders, user must have sufficient credits.
    """
    try:
        order_service = get_order_service()
        
        # Build specifications
        specifications = OrderSpecifications(
            location_code=location_code,
            material_code=material_code,
            quantity=quantity,
            shape=shape,
            adhesive=adhesive,
            core_size=core_size,
            product_type=product_type,
            shipping_method=shipping_method,
        )
        
        # Build shipping address
        shipping_address = ShippingAddress(
            name=shipping_name,
            street=shipping_street,
            city=shipping_city,
            postal_code=shipping_postal_code,
            country=shipping_country,
            phone=shipping_phone,
        )
        
        # Create order
        order = await order_service.create_order(
            user_id=current_user["user_id"],
            order_type=order_type,
            reference=reference,
            specifications=specifications,
            shipping_address=shipping_address,
            pdf_file=pdf_file.file,
            org_id=org_id,
        )
        
        return {
            "ok": True,
            "order": order.dict(),
        }
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("order.create_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create order")


@router.post("/{order_id}/calculate", response_model=dict)
async def calculate_order_price(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Calculate order price using OGOS API.
    """
    try:
        order_service = get_order_service()
        result = await order_service.calculate_order_price(
            order_id=order_id,
            user_id=current_user["user_id"],
        )
        return {"ok": True, **result}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("order.calculate_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to calculate price")


@router.post("/{order_id}/submit", response_model=dict)
async def submit_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Submit order to OGOS API.
    
    For B2C orders, 1 credit will be deducted.
    """
    try:
        order_service = get_order_service()
        result = await order_service.submit_order_to_ogos(
            order_id=order_id,
            user_id=current_user["user_id"],
        )
        return {"ok": True, **result}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("order.submit_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to submit order")


@router.get("", response_model=dict)
async def list_orders(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
):
    """
    List orders for current user.
    """
    try:
        order_service = get_order_service()
        result = await order_service.list_orders(
            user_id=current_user["user_id"],
            limit=limit,
            offset=offset,
        )
        return {
            "ok": True,
            "orders": [order.dict() for order in result["orders"]],
            "total": result["total"],
            "limit": result["limit"],
            "offset": result["offset"],
        }
    
    except Exception as e:
        logger.exception("order.list_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list orders")


@router.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get order details.
    """
    try:
        order_service = get_order_service()
        order = await order_service.get_order(
            order_id=order_id,
            user_id=current_user["user_id"],
        )
        return {"ok": True, "order": order.dict()}
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception("order.get_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get order")


@router.get("/{order_id}/status", response_model=dict)
async def get_order_status(
    order_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get order status (including OGOS order status).
    """
    try:
        order_service = get_order_service()
        order = await order_service.get_order(
            order_id=order_id,
            user_id=current_user["user_id"],
        )
        return {
            "ok": True,
            "order_id": order.order_id,
            "status": order.status.value,
            "ogos_order_id": order.ogos_order_id,
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
        }
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception("order.status_error")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get order status")

