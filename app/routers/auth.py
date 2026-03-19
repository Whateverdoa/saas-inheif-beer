from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import logging

from app.services.auth_service import ClerkAuthService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

logger = logging.getLogger("uvicorn.error")

# Initialize auth service
auth_service = ClerkAuthService()


class LoginRequest(BaseModel):
    """Request model for login endpoint."""
    token: str


@router.post("/login")
async def login(request: LoginRequest) -> Dict[str, Any]:
    """
    Login endpoint that validates a Clerk session token.
    
    This endpoint accepts a Clerk session token (typically obtained from the frontend
    after user authentication) and validates it. Returns user information if valid.
    
    Args:
        request: LoginRequest containing the Clerk session token
        
    Returns:
        Dictionary containing user information and authentication status
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        user_claims = auth_service.verify_token(request.token)
        logger.info("auth.login_success", extra={"user_id": user_claims.get("user_id")})
        return {
            "ok": True,
            "user": user_claims,
            "authenticated": True,
        }
    except ValueError as e:
        logger.warning("auth.login_failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )
    except Exception as e:
        logger.exception("auth.login_error", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error",
        )


@router.post("/logout")
async def logout() -> Dict[str, str]:
    """
    Logout endpoint (optional, primarily handled by Clerk on frontend).
    
    Note: Clerk handles most logout logic on the frontend. This endpoint
    is provided for API consistency but may not be necessary depending on
    your architecture.
    
    Returns:
        Success message
    """
    return {"ok": True, "message": "Logout handled by Clerk frontend"}


@router.get("/me")
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Protected endpoint that requires a valid Bearer token in the Authorization header.
    Returns the user information extracted from the verified token.
    
    Args:
        user: User claims from get_current_user dependency
        
    Returns:
        Dictionary containing current user information
    """
    return {
        "ok": True,
        "user": user,
    }

