import os
import logging
from typing import Any, Dict, Optional
from clerk_backend_api import Clerk

logger = logging.getLogger("uvicorn.error")

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")


def _get_attr_or_dict(obj: Any, key: str, default: Any = None) -> Any:
    """Helper to get attribute from object or dict-like object."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class ClerkAuthService:
    """
    Service for verifying Clerk authentication tokens.
    Uses Clerk's backend SDK to validate JWT tokens and extract user claims.
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or CLERK_SECRET_KEY
        if not self.secret_key:
            logger.warning("CLERK_SECRET_KEY not set - authentication will not work")
        
        self.clerk = Clerk(bearer_auth=self.secret_key) if self.secret_key else None

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a Clerk JWT token and return the decoded claims.
        
        Args:
            token: JWT token string (without 'Bearer ' prefix)
            
        Returns:
            Dictionary containing user claims (user_id, email, etc.)
            
        Raises:
            ValueError: If token is invalid, expired, or verification fails
        """
        if not self.secret_key:
            raise ValueError("CLERK_SECRET_KEY not configured")
        
        if not self.clerk:
            raise ValueError("Clerk client not initialized")
        
        try:
            # Clerk SDK handles token verification
            # Verify the session token
            session = self.clerk.sessions.verify_token(token)
            
            # Extract user_id and session_id (handle both dict and object responses)
            user_id = _get_attr_or_dict(session, "user_id")
            session_id = _get_attr_or_dict(session, "id")
            
            if not user_id:
                raise ValueError("Token missing user_id claim")
            
            # Fetch full user details
            user = self.clerk.users.get(user_id)
            
            # Extract user information (handle both dict and object responses)
            email_addresses = _get_attr_or_dict(user, "email_addresses", [])
            email = None
            if email_addresses and len(email_addresses) > 0:
                first_email = email_addresses[0]
                email = _get_attr_or_dict(first_email, "email_address")
            
            first_name = _get_attr_or_dict(user, "first_name")
            last_name = _get_attr_or_dict(user, "last_name")
            image_url = _get_attr_or_dict(user, "image_url")
            
            return {
                "user_id": user_id,
                "session_id": session_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "image_url": image_url,
            }
        except Exception as e:
            logger.warning(f"Clerk token verification failed: {str(e)}")
            raise ValueError(f"Token verification failed: {str(e)}")

    def get_user_id(self, token: str) -> str:
        """
        Extract user ID from a verified token.
        
        Args:
            token: JWT token string
            
        Returns:
            User ID string
            
        Raises:
            ValueError: If token is invalid or user_id is missing
        """
        claims = self.verify_token(token)
        user_id = claims.get("user_id")
        if not user_id:
            raise ValueError("Token missing user_id claim")
        return user_id

