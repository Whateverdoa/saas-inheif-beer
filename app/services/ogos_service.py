"""Enhanced OGOS API client service."""
import os
import logging
from typing import Any, Dict, List, Optional
import httpx
import asyncio
import math
from pydantic import BaseModel, Field

logger = logging.getLogger("uvicorn.error")

OGOS_BASE_URL = os.getenv("OGOS_BASE_URL", "https://orders.optimumgroup.nl/OrderServiceTest")
OGOS_API_KEY = os.getenv("OGOS_API_KEY", "")
OGOS_MASTER_GUID = os.getenv("OGOS_MASTER_GUID", "")

DEFAULT_TIMEOUT = 30.0
MAX_ATTEMPTS = 4
INITIAL_BACKOFF = 0.8  # seconds


# Request Models
class ShippingAddress(BaseModel):
    """Shipping address model."""
    name: str
    street: str
    city: str
    postal_code: str = Field(alias="postalCode")
    country: str = "NL"
    phone: Optional[str] = None
    
    class Config:
        populate_by_name = True


class OrderSpecifications(BaseModel):
    """Order specifications model."""
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
    """Order calculation request model."""
    guid: str
    specifications: OrderSpecifications
    shipping_address: Optional[ShippingAddress] = Field(None, alias="shippingAddress")
    
    class Config:
        populate_by_name = True


class OrderSubmitRequest(BaseModel):
    """Order submission request model."""
    guid: str
    specifications: OrderSpecifications
    shipping_address: ShippingAddress = Field(alias="shippingAddress")
    pdf_data: bytes = Field(alias="pdfData")
    reference: str
    customer_email: Optional[str] = Field(None, alias="customerEmail")
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True


# Response Models
class OrderCalculateResponse(BaseModel):
    """Order calculation response model."""
    success: bool
    price: Optional[float] = None
    shipping_cost: Optional[float] = None
    total: Optional[float] = None
    currency: str = "EUR"
    estimated_delivery_days: Optional[int] = Field(None, alias="estimatedDeliveryDays")
    errors: Optional[List[str]] = None
    
    class Config:
        populate_by_name = True


class OrderSubmitResponse(BaseModel):
    """Order submission response model."""
    success: bool
    ogos_order_id: Optional[str] = Field(None, alias="ogosOrderId")
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    
    class Config:
        populate_by_name = True


# Material/Config Models
class Location(BaseModel):
    """Location model."""
    code: str
    name: str
    country: Optional[str] = None


class Material(BaseModel):
    """Material model."""
    code: str
    name: str
    description: Optional[str] = None


class OGOSService:
    """Enhanced OGOS API client service."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        master_guid: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize OGOS service.
        
        Args:
            base_url: OGOS API base URL
            api_key: API key for authentication
            master_guid: Master GUID for B2C orders
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or OGOS_BASE_URL).rstrip("/")
        self.api_key = api_key or OGOS_API_KEY
        self.master_guid = master_guid or OGOS_MASTER_GUID
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _request_with_retry(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make request with retry logic."""
        attempt = 0
        exc: Exception | None = None
        
        while attempt < MAX_ATTEMPTS:
            try:
                kwargs = {"headers": self._headers()}
                if json_data:
                    kwargs["json"] = json_data
                if data:
                    kwargs["data"] = data
                if files:
                    kwargs["files"] = files
                
                resp = await self.client.request(method, url, **kwargs)
                
                if 200 <= resp.status_code < 300:
                    return resp.json()
                
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise httpx.HTTPStatusError(
                        f"server_or_rate_error: {resp.status_code}",
                        request=resp.request,
                        response=resp,
                    )
                
                return {"ok": False, "status": resp.status_code, "error": resp.text}
            
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.HTTPStatusError) as e:
                exc = e
                backoff = INITIAL_BACKOFF * math.pow(2, attempt)
                jitter = 0.2 * backoff
                sleep_for = backoff + jitter
                logger.warning(
                    "ogos.retrying",
                    extra={"attempt": attempt + 1, "sleep": sleep_for, "error": str(e)},
                )
                await asyncio.sleep(sleep_for)
                attempt += 1
            
            except Exception as e:
                logger.exception("ogos.unexpected_error")
                return {"ok": False, "error": str(e)}
        
        return {"ok": False, "error": str(exc) if exc else "unknown_error"}
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    # Configuration Endpoints
    async def get_locations(self) -> List[Location]:
        """Get available locations."""
        try:
            url = f"{self.base_url}/api/material/Locations"
            data = await self._request_with_retry("GET", url)
            if isinstance(data, list):
                return [Location(**loc) for loc in data]
            return []
        except Exception as e:
            logger.error(f"Error fetching locations: {e}")
            raise
    
    async def get_materials(self, location_code: str) -> List[Material]:
        """Get available materials for location."""
        try:
            url = f"{self.base_url}/api/material/Material"
            params = {"LocationCode": location_code}
            data = await self._request_with_retry("GET", f"{url}?LocationCode={location_code}")
            if isinstance(data, list):
                return [Material(**mat) for mat in data]
            return []
        except Exception as e:
            logger.error(f"Error fetching materials: {e}")
            raise
    
    async def get_shapes(self, location_code: str) -> List[Dict[str, Any]]:
        """Get available shapes for location."""
        try:
            url = f"{self.base_url}/api/material/shapes"
            data = await self._request_with_retry("GET", f"{url}?LocationCode={location_code}")
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            logger.error(f"Error fetching shapes: {e}")
            raise
    
    async def get_adhesives(self, location_code: str) -> List[Dict[str, Any]]:
        """Get available adhesives for location."""
        try:
            url = f"{self.base_url}/api/material/Adhesives"
            data = await self._request_with_retry("GET", f"{url}?LocationCode={location_code}")
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            logger.error(f"Error fetching adhesives: {e}")
            raise
    
    async def get_shipping_methods(self, location_code: str) -> List[Dict[str, Any]]:
        """Get available shipping methods for location."""
        try:
            url = f"{self.base_url}/api/material/shippingmethods"
            data = await self._request_with_retry("GET", f"{url}?LocationCode={location_code}")
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            logger.error(f"Error fetching shipping methods: {e}")
            raise
    
    # Order Operations
    async def calculate_order(
        self,
        guid: str,
        specifications: OrderSpecifications,
        shipping_address: Optional[ShippingAddress] = None,
    ) -> OrderCalculateResponse:
        """
        Calculate order price.
        
        Args:
            guid: OGOS GUID (org GUID for B2B, master GUID for B2C)
            specifications: Order specifications
            shipping_address: Optional shipping address
            
        Returns:
            OrderCalculateResponse with pricing information
        """
        try:
            request = OrderCalculateRequest(
                guid=guid,
                specifications=specifications,
                shipping_address=shipping_address,
            )
            payload = request.model_dump(by_alias=True, exclude_none=True)
            
            url = f"{self.base_url}/api/order/calculate"
            data = await self._request_with_retry("POST", url, json_data=payload)
            
            if data.get("ok") is False:
                return OrderCalculateResponse(
                    success=False,
                    errors=[data.get("error", "Unknown error")],
                )
            
            return OrderCalculateResponse(**data)
        
        except Exception as e:
            logger.error(f"Error calculating order: {e}")
            return OrderCalculateResponse(
                success=False,
                errors=[str(e)],
            )
    
    async def submit_order(
        self,
        guid: str,
        specifications: OrderSpecifications,
        shipping_address: ShippingAddress,
        pdf_data: bytes,
        reference: str,
        customer_email: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> OrderSubmitResponse:
        """
        Submit order to OGOS.
        
        Args:
            guid: OGOS GUID (org GUID for B2B, master GUID for B2C)
            specifications: Order specifications
            shipping_address: Shipping address
            pdf_data: PDF file bytes
            reference: Order reference
            customer_email: Optional customer email
            notes: Optional notes
            
        Returns:
            OrderSubmitResponse with OGOS order ID
        """
        try:
            files = {
                "pdf": ("order.pdf", pdf_data, "application/pdf"),
            }
            
            data = {
                "guid": guid,
                "reference": reference,
                **specifications.model_dump(by_alias=True, exclude_none=True),
                **shipping_address.model_dump(by_alias=True),
            }
            
            if customer_email:
                data["customerEmail"] = customer_email
            if notes:
                data["notes"] = notes
            
            url = f"{self.base_url}/api/order"
            result = await self._request_with_retry("POST", url, data=data, files=files)
            
            if result.get("ok") is False:
                return OrderSubmitResponse(
                    success=False,
                    errors=[result.get("error", "Unknown error")],
                )
            
            return OrderSubmitResponse(
                success=True,
                ogos_order_id=result.get("orderId"),
                message=result.get("message"),
            )
        
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            return OrderSubmitResponse(
                success=False,
                errors=[str(e)],
            )
    
    async def get_dummy_calculation(self) -> Dict[str, Any]:
        """Get dummy calculation for testing."""
        try:
            url = f"{self.base_url}/api/order/dummycalculation"
            return await self._request_with_retry("GET", url)
        except Exception as e:
            logger.error(f"Error getting dummy calculation: {e}")
            raise


# Singleton instance
_ogos_service: Optional[OGOSService] = None


def get_ogos_service() -> OGOSService:
    """Get OGOS service singleton instance."""
    global _ogos_service
    if _ogos_service is None:
        _ogos_service = OGOSService()
    return _ogos_service

