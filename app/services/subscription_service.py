"""Subscription management service."""
import logging
from typing import Optional
from datetime import datetime

from app.models import Subscription, SubscriptionStatus
from app.services.database import get_database

logger = logging.getLogger("uvicorn.error")


class SubscriptionService:
    """Subscription management service."""
    
    def __init__(self):
        self.db = get_database()
    
    async def validate_subscription_active(self, org_id: str) -> bool:
        """
        Validate that organization has an active subscription.
        
        Args:
            org_id: Organization ID
            
        Returns:
            True if subscription is active, False otherwise
        """
        subscription = await self.db.get_subscription_by_org(org_id)
        if not subscription:
            return False
        
        if subscription.status != SubscriptionStatus.ACTIVE:
            return False
        
        # Check if subscription period is still valid
        if subscription.current_period_end < datetime.now():
            return False
        
        return True
    
    async def get_organization_subscription(self, org_id: str) -> Optional[Subscription]:
        """
        Get subscription for organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Subscription or None
        """
        return await self.db.get_subscription_by_org(org_id)
    
    async def sync_subscription_status(
        self,
        polar_subscription_id: str,
        status: SubscriptionStatus,
        **updates,
    ) -> Optional[Subscription]:
        """
        Sync subscription status from Polar webhook.
        
        Args:
            polar_subscription_id: Polar subscription ID
            status: New status
            **updates: Additional fields to update
            
        Returns:
            Updated subscription or None
        """
        # Find subscription by polar_subscription_id
        # This would require a new method in database adapter
        # For now, return None (to be implemented)
        logger.warning("sync_subscription_status not fully implemented")
        return None


# Singleton instance
_subscription_service: Optional[SubscriptionService] = None


def get_subscription_service() -> SubscriptionService:
    """Get subscription service singleton instance."""
    global _subscription_service
    if _subscription_service is None:
        _subscription_service = SubscriptionService()
    return _subscription_service

