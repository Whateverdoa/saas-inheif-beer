from fastapi import Header, HTTPException, status
from typing import Optional, Dict, Any
import logging

from app.services.auth_service import ClerkAuthService

logger = logging.getLogger("uvicorn.error")

# Initialize auth service singleton
_auth_service = ClerkAuthService()


async def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and verify Clerk authentication token.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: Dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    
    Args:
        authorization: Authorization header value (expected format: "Bearer <token>")
        
    Returns:
        Dictionary containing user claims (user_id, email, etc.)
        
    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    
    try:
        user_claims = _auth_service.verify_token(token)
        return user_claims
    except ValueError as e:
        logger.warning("auth.verification_failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.exception("auth.unexpected_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

