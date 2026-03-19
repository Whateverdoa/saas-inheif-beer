"""Credit management service for B2C."""
import logging
from typing import Optional
from decimal import Decimal

from app.models import Credit
from app.services.database import get_database

logger = logging.getLogger("uvicorn.error")


class CreditService:
    """Credit management service."""
    
    def __init__(self):
        self.db = get_database()
    
    async def get_credit_balance(self, user_id: str) -> Decimal:
        """
        Get credit balance for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Credit balance
        """
        return await self.db.get_credit_balance(user_id)
    
    async def purchase_credits(
        self,
        user_id: str,
        amount: Decimal,
        transaction_id: str,
    ) -> Credit:
        """
        Add credits to user balance.
        
        Args:
            user_id: User ID
            amount: Credit amount to add
            transaction_id: Transaction ID from payment
            
        Returns:
            Updated credit record
        """
        credit = Credit(
            user_id=user_id,
            amount=amount,
            transaction_id=transaction_id,
        )
        return await self.db.create_credit(credit)
    
    async def deduct_credit(self, user_id: str, amount: Decimal = Decimal("1")) -> bool:
        """
        Deduct credits from user balance.
        
        Args:
            user_id: User ID
            amount: Amount to deduct (default: 1)
            
        Returns:
            True if successful, False if insufficient credits
        """
        return await self.db.deduct_credit(user_id, amount)
    
    async def validate_sufficient_credits(self, user_id: str, required: Decimal = Decimal("1")) -> bool:
        """
        Validate user has sufficient credits.
        
        Args:
            user_id: User ID
            required: Required credit amount (default: 1)
            
        Returns:
            True if sufficient credits, False otherwise
        """
        balance = await self.get_credit_balance(user_id)
        return balance >= required


# Singleton instance
_credit_service: Optional[CreditService] = None


def get_credit_service() -> CreditService:
    """Get credit service singleton instance."""
    global _credit_service
    if _credit_service is None:
        _credit_service = CreditService()
    return _credit_service

