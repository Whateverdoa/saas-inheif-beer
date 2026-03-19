# app/integrations/ogos.py
"""
OGOS API Client voor Optimum Group Order Service
"""
import httpx
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Request Models
class ShippingAddress(BaseModel):
    name: str
    street: str
    city: str
    postal_code: str = Field(alias="postalCode")
    country: str
    phone: Optional[str] = None


class OrderSpecifications(BaseModel):
    location_code: str = Field(alias="locationCode")
    material_code: Optional[str] = Field(None, alias="materialCode")
    quantity: int
    shape: Optional[str] = None
    adhesive: Optional[str] = None
    core_size: Optional[str] = Field(None, alias="coreSize")
    product_type: Optional[str] = Field(None, alias="productType")
    shipping_method: Optional[str] = Field(None, alias="shippingMethod")
    
    class Config:
        populate_by_name = True


class OrderCalculateRequest(BaseModel):
    guid: str
    specifications: OrderSpecifications
    shipping_address: Optional[ShippingAddress] = Field(None, alias="shippingAddress")


class OrderSubmitRequest(BaseModel):
    guid: str
    specifications: OrderSpecifications
    shipping_address: ShippingAddress = Field(alias="shippingAddress")
    pdf_data: bytes = Field(alias="pdfData")  # Base64 of binary
    reference: str  # Jouw order reference
    customer_email: Optional[str] = Field(None, alias="customerEmail")
    notes: Optional[str] = None


# Response Models
class OrderCalculateResponse(BaseModel):
    success: bool
    price: Optional[float] = None
    shipping_cost: Optional[float] = None
    total: Optional[float] = None
    currency: str = "EUR"
    estimated_delivery_days: Optional[int] = Field(None, alias="estimatedDeliveryDays")
    errors: Optional[List[str]] = None


class OrderSubmitResponse(BaseModel):
    success: bool
    ogos_order_id: Optional[str] = Field(None, alias="ogosOrderId")
    message: Optional[str] = None
    errors: Optional[List[str]] = None


# Material/Config Models
class Location(BaseModel):
    code: str
    name: str
    country: Optional[str] = None


class Material(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class OGOSClient:
    """
    Client voor OGOS API communicatie
    """
    
    def __init__(
        self,
        base_url: str = "https://orders.optimumgroup.nl/OrderServiceTest",
        timeout: float = 30.0,
        master_guid: Optional[str] = None,  # Voor B2C orders
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.master_guid = master_guid
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def close(self):
        await self.client.aclose()
    
    # Configuration Endpoints
    async def get_locations(self) -> List[Location]:
        """Haal beschikbare locaties op"""
        try:
            response = await self.client.get(f"{self.base_url}/api/material/Locations")
            response.raise_for_status()
            data = response.json()
            return [Location(**loc) for loc in data]
        except Exception as e:
            logger.error(f"Error fetching locations: {e}")
            raise
    
    async def get_materials(self, location_code: str) -> List[Material]:
        """Haal beschikbare materialen voor locatie op"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/material/Material",
                params={"LocationCode": location_code}
            )
            response.raise_for_status()
            data = response.json()
            return [Material(**mat) for mat in data]
        except Exception as e:
            logger.error(f"Error fetching materials: {e}")
            raise
    
    async def get_shapes(self, location_code: str) -> List[Dict[str, Any]]:
        """Haal beschikbare vormen op"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/material/shapes",
                params={"LocationCode": location_code}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching shapes: {e}")
            raise
    
    async def get_adhesives(self, location_code: str) -> List[Dict[str, Any]]:
        """Haal beschikbare lijmsoorten op"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/material/Adhesives",
                params={"LocationCode": location_code}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching adhesives: {e}")
            raise
    
    async def get_shipping_methods(self, location_code: str) -> List[Dict[str, Any]]:
        """Haal beschikbare verzendmethoden op"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/material/shippingmethods",
                params={"LocationCode": location_code}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching shipping methods: {e}")
            raise
    
    # Order Operations
    async def calculate_order(
        self,
        request: OrderCalculateRequest,
    ) -> OrderCalculateResponse:
        """
        Bereken orderprijs vooraf
        """
        try:
            payload = request.model_dump(by_alias=True, exclude_none=True)
            
            response = await self.client.post(
                f"{self.base_url}/api/order/calculate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            return OrderCalculateResponse(**data)
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during order calculation: {e}")
            return OrderCalculateResponse(
                success=False,
                errors=[f"API error: {e.response.status_code}"]
            )
        except Exception as e:
            logger.error(f"Error calculating order: {e}")
            return OrderCalculateResponse(
                success=False,
                errors=[str(e)]
            )
    
    async def submit_order(
        self,
        request: OrderSubmitRequest,
    ) -> OrderSubmitResponse:
        """
        Plaats order bij OGOS
        """
        try:
            # Prepare multipart form data with PDF
            files = {
                'pdf': ('order.pdf', request.pdf_data, 'application/pdf')
            }
            
            data = {
                'guid': request.guid,
                'reference': request.reference,
                **request.specifications.model_dump(by_alias=True, exclude_none=True),
                **request.shipping_address.model_dump(by_alias=True),
            }
            
            if request.customer_email:
                data['customerEmail'] = request.customer_email
            if request.notes:
                data['notes'] = request.notes
            
            response = await self.client.post(
                f"{self.base_url}/api/order",
                data=data,
                files=files,
            )
            response.raise_for_status()
            result = response.json()
            
            return OrderSubmitResponse(
                success=True,
                ogos_order_id=result.get('orderId'),
                message=result.get('message'),
            )
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during order submission: {e}")
            error_detail = e.response.text
            return OrderSubmitResponse(
                success=False,
                errors=[f"API error {e.response.status_code}: {error_detail}"]
            )
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            return OrderSubmitResponse(
                success=False,
                errors=[str(e)]
            )
    
    async def get_dummy_calculation(self) -> Dict[str, Any]:
        """
        Test endpoint voor dummy berekening
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/order/dummycalculation"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting dummy calculation: {e}")
            raise


# Singleton instance (optioneel)
_ogos_client: Optional[OGOSClient] = None


def get_ogos_client(master_guid: Optional[str] = None) -> OGOSClient:
    """
    Get of maak OGOS client instance
    """
    global _ogos_client
    if _ogos_client is None:
        _ogos_client = OGOSClient(master_guid=master_guid)
    return _ogos_client
