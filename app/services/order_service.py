"""Order management service."""
import os
import logging
from typing import Optional, BinaryIO, Dict, Any
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.models import Order, OrderType, OrderStatus, OrderSpecifications, ShippingAddress
from app.services.database import get_database
from app.services.pdf_validator import get_pdf_validator
from app.services.ogos_service import get_ogos_service, OrderSpecifications as OGOSOrderSpecifications, ShippingAddress as OGOSShippingAddress
from app.services.subscription_service import get_subscription_service
from app.services.credit_service import get_credit_service

logger = logging.getLogger("uvicorn.error")

# File storage configuration
# Use /tmp on Vercel (serverless) as it's the only writable directory
_default_upload_dir = "/tmp/uploads" if os.getenv("VERCEL") else "./uploads"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", _default_upload_dir))

def _ensure_upload_dir():
    """Create upload directory if it doesn't exist (called lazily, not at import)."""
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


class OrderService:
    """Order management service."""
    
    def __init__(self):
        self.db = get_database()
        self.pdf_validator = get_pdf_validator()
        self.ogos_service = get_ogos_service()
        self.subscription_service = get_subscription_service()
        self.credit_service = get_credit_service()
    
    async def create_order(
        self,
        user_id: str,
        order_type: OrderType,
        reference: str,
        specifications: OrderSpecifications,
        shipping_address: ShippingAddress,
        pdf_file: BinaryIO,
        org_id: Optional[str] = None,
    ) -> Order:
        """
        Create a new order with PDF upload and validation.
        
        Args:
            user_id: User ID
            order_type: Order type (b2b or b2c)
            reference: Order reference
            specifications: Order specifications
            shipping_address: Shipping address
            pdf_file: PDF file
            org_id: Organization ID (required for B2B)
            
        Returns:
            Created Order
            
        Raises:
            ValueError: If validation fails or requirements not met
        """
        # Validate B2B requirements
        if order_type == OrderType.B2B:
            if not org_id:
                raise ValueError("Organization ID required for B2B orders")
            
            # Check subscription status
            org = await self.db.get_organization(org_id)
            if not org:
                raise ValueError("Organization not found")
            
            if org.user_id != user_id:
                raise ValueError("User does not own this organization")
            
            # Validate subscription is active
            is_active = await self.subscription_service.validate_subscription_active(org_id)
            if not is_active:
                raise ValueError("Organization subscription is not active")
            
            # Check rate limiting
            orders_today = await self.db.get_orders_count_today(org_id)
            if orders_today >= org.rate_limit_per_day:
                raise ValueError(f"Rate limit exceeded: {org.rate_limit_per_day} orders per day")
            
            ogos_guid = org.ogos_guid
        else:
            # B2C: Check credit balance
            balance = await self.credit_service.get_credit_balance(user_id)
            if balance < Decimal("1"):
                raise ValueError("Insufficient credits. Please purchase credits first.")
            
            ogos_guid = self.ogos_service.master_guid
            if not ogos_guid:
                raise ValueError("Master GUID not configured")
        
        # Read PDF data
        pdf_data = pdf_file.read()
        
        # Validate PDF
        validation_result = self.pdf_validator.validate(pdf_data)
        if not validation_result.is_valid:
            raise ValueError(f"PDF validation failed: {', '.join(validation_result.errors)}")
        
        # Store PDF file
        _ensure_upload_dir()
        pdf_filename = f"{reference}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = UPLOAD_DIR / pdf_filename
        pdf_path.write_bytes(pdf_data)
        pdf_url = str(pdf_path.relative_to(Path.cwd()))
        
        # Create order
        order = Order(
            user_id=user_id,
            org_id=org_id,
            order_type=order_type,
            reference=reference,
            specifications=specifications,
            shipping_address=shipping_address,
            pdf_url=pdf_url,
            pdf_metadata=validation_result,
            ogos_guid_used=ogos_guid,
            status=OrderStatus.PENDING,
        )
        
        # Save to database
        order = await self.db.create_order(order)
        
        logger.info(
            "order.created",
            extra={
                "order_id": order.order_id,
                "user_id": user_id,
                "order_type": order_type.value,
                "reference": reference,
            },
        )
        
        return order
    
    async def calculate_order_price(
        self,
        order_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Calculate order price using OGOS API.
        
        Args:
            order_id: Order ID
            user_id: User ID (for authorization)
            
        Returns:
            Dictionary with pricing information
            
        Raises:
            ValueError: If order not found or not authorized
        """
        order = await self.db.get_order(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.user_id != user_id:
            raise ValueError("Not authorized")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError("Order already submitted")
        
        # Convert to OGOS models
        ogos_specs = OGOSOrderSpecifications(
            location_code=order.specifications.location_code,
            material_code=order.specifications.material_code,
            quantity=order.specifications.quantity,
            shape=order.specifications.shape,
            adhesive=order.specifications.adhesive,
            core_size=order.specifications.core_size,
            product_type=order.specifications.product_type,
            shipping_method=order.specifications.shipping_method,
        )
        
        ogos_shipping = OGOSShippingAddress(
            name=order.shipping_address.name,
            street=order.shipping_address.street,
            city=order.shipping_address.city,
            postal_code=order.shipping_address.postal_code,
            country=order.shipping_address.country,
            phone=order.shipping_address.phone,
        )
        
        # Calculate price
        result = await self.ogos_service.calculate_order(
            guid=order.ogos_guid_used,
            specifications=ogos_specs,
            shipping_address=ogos_shipping,
        )
        
        if not result.success:
            raise ValueError(f"Price calculation failed: {', '.join(result.errors or [])}")
        
        # Update order with pricing
        await self.db.update_order(
            order_id,
            price_calculated=result.price,
            shipping_cost=result.shipping_cost,
            total=result.total,
            currency=result.currency,
        )
        
        return {
            "success": True,
            "price": result.price,
            "shipping_cost": result.shipping_cost,
            "total": result.total,
            "currency": result.currency,
            "estimated_delivery_days": result.estimated_delivery_days,
        }
    
    async def submit_order_to_ogos(
        self,
        order_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Submit order to OGOS API.
        
        Args:
            order_id: Order ID
            user_id: User ID (for authorization)
            
        Returns:
            Dictionary with submission result
            
        Raises:
            ValueError: If order not found, not authorized, or submission fails
        """
        order = await self.db.get_order(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.user_id != user_id:
            raise ValueError("Not authorized")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError("Order already submitted")
        
        # For B2C, deduct credit before submission
        if order.order_type == OrderType.B2C:
            success = await self.credit_service.deduct_credit(user_id, Decimal("1"))
            if not success:
                raise ValueError("Failed to deduct credit")
        
        # Read PDF file
        if not order.pdf_url:
            raise ValueError("PDF file not found")
        
        pdf_path = Path(order.pdf_url)
        if not pdf_path.exists():
            # Try absolute path
            pdf_path = UPLOAD_DIR / Path(order.pdf_url).name
            if not pdf_path.exists():
                raise ValueError("PDF file not found")
        
        pdf_data = pdf_path.read_bytes()
        
        # Convert to OGOS models
        ogos_specs = OGOSOrderSpecifications(
            location_code=order.specifications.location_code,
            material_code=order.specifications.material_code,
            quantity=order.specifications.quantity,
            shape=order.specifications.shape,
            adhesive=order.specifications.adhesive,
            core_size=order.specifications.core_size,
            product_type=order.specifications.product_type,
            shipping_method=order.specifications.shipping_method,
        )
        
        ogos_shipping = OGOSShippingAddress(
            name=order.shipping_address.name,
            street=order.shipping_address.street,
            city=order.shipping_address.city,
            postal_code=order.shipping_address.postal_code,
            country=order.shipping_address.country,
            phone=order.shipping_address.phone,
        )
        
        # Submit to OGOS
        result = await self.ogos_service.submit_order(
            guid=order.ogos_guid_used,
            specifications=ogos_specs,
            shipping_address=ogos_shipping,
            pdf_data=pdf_data,
            reference=order.reference,
        )
        
        if not result.success:
            # Refund credit if B2C
            if order.order_type == OrderType.B2C:
                from app.models import Credit
                refund_credit = Credit(
                    user_id=user_id,
                    amount=Decimal("1"),
                )
                await self.credit_service.create_credit(refund_credit)
            raise ValueError(f"Order submission failed: {', '.join(result.errors or [])}")
        
        # Update order status
        await self.db.update_order(
            order_id,
            ogos_order_id=result.ogos_order_id,
            status=OrderStatus.SUBMITTED,
            submitted_at=datetime.now(),
        )
        
        logger.info(
            "order.submitted",
            extra={
                "order_id": order_id,
                "ogos_order_id": result.ogos_order_id,
            },
        )
        
        return {
            "success": True,
            "ogos_order_id": result.ogos_order_id,
            "message": result.message,
        }
    
    async def get_order(self, order_id: str, user_id: str) -> Order:
        """
        Get order by ID (with authorization check).
        
        Args:
            order_id: Order ID
            user_id: User ID (for authorization)
            
        Returns:
            Order
            
        Raises:
            ValueError: If order not found or not authorized
        """
        order = await self.db.get_order(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.user_id != user_id:
            raise ValueError("Not authorized")
        
        return order
    
    async def list_orders(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List orders for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of orders to return
            offset: Offset for pagination
            
        Returns:
            Dictionary with orders and pagination info
        """
        return await self.db.get_orders_by_user(user_id, limit=limit, offset=offset)


# Singleton instance
_order_service: Optional[OrderService] = None


def get_order_service() -> OrderService:
    """Get order service singleton instance."""
    global _order_service
    if _order_service is None:
        _order_service = OrderService()
    return _order_service

