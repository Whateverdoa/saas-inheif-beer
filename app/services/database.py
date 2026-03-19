"""Database abstraction layer for SQLite (local) and Convex (production)."""
import os
import logging
from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Numeric, Text, JSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.models import (
    User, UserRole,
    Organization, OrgSubscriptionStatus,
    Order, OrderType, OrderStatus,
    Subscription, SubscriptionStatus,
    Credit,
    Transaction, TransactionStatus, TransactionProvider,
)

logger = logging.getLogger("uvicorn.error")

Base = declarative_base()


# SQLAlchemy Models
class UserModel(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.B2C_CUSTOMER)
    extra_data = Column("metadata", SQLiteJSON, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class OrganizationModel(Base):
    __tablename__ = "organizations"
    org_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    kvk_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    ogos_guid = Column(String, nullable=False)
    subscription_id = Column(String, nullable=True)
    subscription_status = Column(SQLEnum(OrgSubscriptionStatus), nullable=False, default=OrgSubscriptionStatus.EXPIRED)
    rate_limit_per_day = Column(Integer, nullable=False, default=100)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class OrderModel(Base):
    __tablename__ = "orders"
    order_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    org_id = Column(String, nullable=True, index=True)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    ogos_order_id = Column(String, nullable=True)
    reference = Column(String, nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    pdf_url = Column(String, nullable=True)
    pdf_metadata = Column(SQLiteJSON, nullable=True)
    specifications = Column(SQLiteJSON, nullable=False)
    shipping_address = Column(SQLiteJSON, nullable=False)
    price_calculated = Column(Numeric(10, 2), nullable=True)
    shipping_cost = Column(Numeric(10, 2), nullable=True)
    total = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=False, default="EUR")
    payment_id = Column(String, nullable=True)
    ogos_guid_used = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    submitted_at = Column(DateTime, nullable=True)
    extra_data = Column("metadata", SQLiteJSON, nullable=False, default={})


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"
    subscription_id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)
    polar_subscription_id = Column(String, nullable=False, unique=True)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.EXPIRED)
    plan_name = Column(String, nullable=False)
    plan_price = Column(Numeric(10, 2), nullable=False)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class CreditModel(Base):
    __tablename__ = "credits"
    credit_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_id = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class TransactionModel(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    org_id = Column(String, nullable=True, index=True)
    order_id = Column(String, nullable=True, index=True)
    provider = Column(SQLEnum(TransactionProvider), nullable=False)
    provider_transaction_id = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, nullable=False, default="EUR")
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    extra_data = Column("metadata", SQLiteJSON, nullable=False, default={})
    created_at = Column(DateTime, nullable=False, default=datetime.now)


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters."""
    
    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def create_organization(self, org: Organization) -> Organization:
        """Create a new organization."""
        pass
    
    @abstractmethod
    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        pass
    
    @abstractmethod
    async def get_organizations_by_user(self, user_id: str) -> List[Organization]:
        """Get all organizations for a user."""
        pass
    
    @abstractmethod
    async def update_organization(self, org_id: str, **updates) -> Optional[Organization]:
        """Update organization."""
        pass
    
    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        """Create a new order."""
        pass
    
    @abstractmethod
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        pass
    
    @abstractmethod
    async def get_orders_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get orders for a user with pagination."""
        pass
    
    @abstractmethod
    async def update_order(self, order_id: str, **updates) -> Optional[Order]:
        """Update order."""
        pass
    
    @abstractmethod
    async def create_subscription(self, subscription: Subscription) -> Subscription:
        """Create a new subscription."""
        pass
    
    @abstractmethod
    async def get_subscription_by_org(self, org_id: str) -> Optional[Subscription]:
        """Get subscription for organization."""
        pass
    
    @abstractmethod
    async def update_subscription(self, subscription_id: str, **updates) -> Optional[Subscription]:
        """Update subscription."""
        pass
    
    @abstractmethod
    async def create_credit(self, credit: Credit) -> Credit:
        """Create or update credit balance."""
        pass
    
    @abstractmethod
    async def get_credit_balance(self, user_id: str) -> Decimal:
        """Get credit balance for user."""
        pass
    
    @abstractmethod
    async def deduct_credit(self, user_id: str, amount: Decimal) -> bool:
        """Deduct credits from user balance."""
        pass
    
    @abstractmethod
    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """Create a new transaction."""
        pass
    
    @abstractmethod
    async def get_orders_count_today(self, org_id: str) -> int:
        """Get count of orders submitted today for rate limiting."""
        pass


class SQLiteAdapter(DatabaseAdapter):
    """SQLite adapter for local development."""
    
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./local.db"):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
    
    async def init_db(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def _model_to_user(self, model: UserModel) -> User:
        """Convert UserModel to User."""
        return User(
            user_id=model.user_id,
            email=model.email,
            name=model.name,
            role=model.role,
            metadata=model.extra_data or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    async def _model_to_org(self, model: OrganizationModel) -> Organization:
        """Convert OrganizationModel to Organization."""
        return Organization(
            org_id=model.org_id,
            user_id=model.user_id,
            name=model.name,
            kvk_number=model.kvk_number,
            address=model.address,
            contact_email=model.contact_email,
            ogos_guid=model.ogos_guid,
            subscription_id=model.subscription_id,
            subscription_status=model.subscription_status,
            rate_limit_per_day=model.rate_limit_per_day,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    async def _model_to_order(self, model: OrderModel) -> Order:
        """Convert OrderModel to Order."""
        from app.models.order import OrderSpecifications, ShippingAddress
        from app.models.pdf_validation import PDFValidationResult
        
        pdf_metadata = None
        if model.pdf_metadata:
            pdf_metadata = PDFValidationResult(**model.pdf_metadata)
        
        return Order(
            order_id=model.order_id,
            user_id=model.user_id,
            org_id=model.org_id,
            order_type=model.order_type,
            ogos_order_id=model.ogos_order_id,
            reference=model.reference,
            status=model.status,
            pdf_url=model.pdf_url,
            pdf_metadata=pdf_metadata,
            specifications=OrderSpecifications(**model.specifications),
            shipping_address=ShippingAddress(**model.shipping_address),
            price_calculated=float(model.price_calculated) if model.price_calculated else None,
            shipping_cost=float(model.shipping_cost) if model.shipping_cost else None,
            total=float(model.total) if model.total else None,
            currency=model.currency,
            payment_id=model.payment_id,
            ogos_guid_used=model.ogos_guid_used,
            created_at=model.created_at,
            updated_at=model.updated_at,
            submitted_at=model.submitted_at,
            metadata=model.extra_data or {},
        )
    
    async def create_user(self, user: User) -> User:
        async with self.async_session() as session:
            db_user = UserModel(
                user_id=user.user_id,
                email=user.email,
                name=user.name,
                role=user.role,
                extra_data=user.metadata,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            return await self._model_to_user(db_user)
    
    async def get_user(self, user_id: str) -> Optional[User]:
        async with self.async_session() as session:
            result = await session.get(UserModel, user_id)
            if result:
                return await self._model_to_user(result)
            return None
    
    async def create_organization(self, org: Organization) -> Organization:
        async with self.async_session() as session:
            db_org = OrganizationModel(
                org_id=org.org_id,
                user_id=org.user_id,
                name=org.name,
                kvk_number=org.kvk_number,
                address=org.address,
                contact_email=org.contact_email,
                ogos_guid=org.ogos_guid,
                subscription_id=org.subscription_id,
                subscription_status=org.subscription_status,
                rate_limit_per_day=org.rate_limit_per_day,
                created_at=org.created_at,
                updated_at=org.updated_at,
            )
            session.add(db_org)
            await session.commit()
            await session.refresh(db_org)
            return await self._model_to_org(db_org)
    
    async def get_organization(self, org_id: str) -> Optional[Organization]:
        async with self.async_session() as session:
            result = await session.get(OrganizationModel, org_id)
            if result:
                return await self._model_to_org(result)
            return None
    
    async def get_organizations_by_user(self, user_id: str) -> List[Organization]:
        async with self.async_session() as session:
            from sqlalchemy import select
            stmt = select(OrganizationModel).where(OrganizationModel.user_id == user_id)
            result = await session.execute(stmt)
            orgs = result.scalars().all()
            return [await self._model_to_org(org) for org in orgs]
    
    async def update_organization(self, org_id: str, **updates) -> Optional[Organization]:
        async with self.async_session() as session:
            org = await session.get(OrganizationModel, org_id)
            if not org:
                return None
            for key, value in updates.items():
                if hasattr(org, key):
                    setattr(org, key, value)
            org.updated_at = datetime.now()
            await session.commit()
            await session.refresh(org)
            return await self._model_to_org(org)
    
    async def create_order(self, order: Order) -> Order:
        async with self.async_session() as session:
            from decimal import Decimal
            
            db_order = OrderModel(
                order_id=order.order_id,
                user_id=order.user_id,
                org_id=order.org_id,
                order_type=order.order_type,
                ogos_order_id=order.ogos_order_id,
                reference=order.reference,
                status=order.status,
                pdf_url=order.pdf_url,
                pdf_metadata=order.pdf_metadata.dict() if order.pdf_metadata else None,
                specifications=order.specifications.dict(),
                shipping_address=order.shipping_address.dict(),
                price_calculated=Decimal(str(order.price_calculated)) if order.price_calculated else None,
                shipping_cost=Decimal(str(order.shipping_cost)) if order.shipping_cost else None,
                total=Decimal(str(order.total)) if order.total else None,
                currency=order.currency,
                payment_id=order.payment_id,
                ogos_guid_used=order.ogos_guid_used,
                created_at=order.created_at,
                updated_at=order.updated_at,
                submitted_at=order.submitted_at,
                extra_data=order.metadata,
            )
            session.add(db_order)
            await session.commit()
            await session.refresh(db_order)
            return await self._model_to_order(db_order)
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        async with self.async_session() as session:
            result = await session.get(OrderModel, order_id)
            if result:
                return await self._model_to_order(result)
            return None
    
    async def get_orders_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        async with self.async_session() as session:
            from sqlalchemy import select, func
            stmt = select(OrderModel).where(OrderModel.user_id == user_id).order_by(OrderModel.created_at.desc())
            count_stmt = select(func.count()).select_from(OrderModel).where(OrderModel.user_id == user_id)
            
            total_result = await session.execute(count_stmt)
            total = total_result.scalar() or 0
            
            result = await session.execute(stmt.offset(offset).limit(limit))
            orders = result.scalars().all()
            
            return {
                "orders": [await self._model_to_order(order) for order in orders],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
    
    async def update_order(self, order_id: str, **updates) -> Optional[Order]:
        async with self.async_session() as session:
            from decimal import Decimal
            order = await session.get(OrderModel, order_id)
            if not order:
                return None
            for key, value in updates.items():
                if hasattr(order, key):
                    if key in ("price_calculated", "shipping_cost", "total") and value is not None:
                        setattr(order, key, Decimal(str(value)))
                    else:
                        setattr(order, key, value)
            order.updated_at = datetime.now()
            await session.commit()
            await session.refresh(order)
            return await self._model_to_order(order)
    
    async def create_subscription(self, subscription: Subscription) -> Subscription:
        async with self.async_session() as session:
            from decimal import Decimal
            db_sub = SubscriptionModel(
                subscription_id=subscription.subscription_id,
                org_id=subscription.org_id,
                polar_subscription_id=subscription.polar_subscription_id,
                status=subscription.status,
                plan_name=subscription.plan_name,
                plan_price=Decimal(str(subscription.plan_price)),
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at,
            )
            session.add(db_sub)
            await session.commit()
            await session.refresh(db_sub)
            return Subscription(
                subscription_id=db_sub.subscription_id,
                org_id=db_sub.org_id,
                polar_subscription_id=db_sub.polar_subscription_id,
                status=db_sub.status,
                plan_name=db_sub.plan_name,
                plan_price=float(db_sub.plan_price),
                current_period_start=db_sub.current_period_start,
                current_period_end=db_sub.current_period_end,
                created_at=db_sub.created_at,
                updated_at=db_sub.updated_at,
            )
    
    async def get_subscription_by_org(self, org_id: str) -> Optional[Subscription]:
        async with self.async_session() as session:
            from sqlalchemy import select
            stmt = select(SubscriptionModel).where(SubscriptionModel.org_id == org_id)
            result = await session.execute(stmt)
            sub = result.scalar_one_or_none()
            if sub:
                return Subscription(
                    subscription_id=sub.subscription_id,
                    org_id=sub.org_id,
                    polar_subscription_id=sub.polar_subscription_id,
                    status=sub.status,
                    plan_name=sub.plan_name,
                    plan_price=float(sub.plan_price),
                    current_period_start=sub.current_period_start,
                    current_period_end=sub.current_period_end,
                    created_at=sub.created_at,
                    updated_at=sub.updated_at,
                )
            return None
    
    async def update_subscription(self, subscription_id: str, **updates) -> Optional[Subscription]:
        async with self.async_session() as session:
            from decimal import Decimal
            sub = await session.get(SubscriptionModel, subscription_id)
            if not sub:
                return None
            for key, value in updates.items():
                if hasattr(sub, key):
                    if key == "plan_price" and value is not None:
                        setattr(sub, key, Decimal(str(value)))
                    else:
                        setattr(sub, key, value)
            sub.updated_at = datetime.now()
            await session.commit()
            await session.refresh(sub)
            return Subscription(
                subscription_id=sub.subscription_id,
                org_id=sub.org_id,
                polar_subscription_id=sub.polar_subscription_id,
                status=sub.status,
                plan_name=sub.plan_name,
                plan_price=float(sub.plan_price),
                current_period_start=sub.current_period_start,
                current_period_end=sub.current_period_end,
                created_at=sub.created_at,
                updated_at=sub.updated_at,
            )
    
    async def create_credit(self, credit: Credit) -> Credit:
        async with self.async_session() as session:
            from decimal import Decimal
            # Check if credit exists for user
            from sqlalchemy import select
            stmt = select(CreditModel).where(CreditModel.user_id == credit.user_id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                existing.amount += Decimal(str(credit.amount))
                existing.updated_at = datetime.now()
                await session.commit()
                await session.refresh(existing)
                return Credit(
                    credit_id=existing.credit_id,
                    user_id=existing.user_id,
                    amount=float(existing.amount),
                    transaction_id=existing.transaction_id,
                    expires_at=existing.expires_at,
                    created_at=existing.created_at,
                    updated_at=existing.updated_at,
                )
            else:
                db_credit = CreditModel(
                    credit_id=credit.credit_id,
                    user_id=credit.user_id,
                    amount=Decimal(str(credit.amount)),
                    transaction_id=credit.transaction_id,
                    expires_at=credit.expires_at,
                    created_at=credit.created_at,
                    updated_at=credit.updated_at,
                )
                session.add(db_credit)
                await session.commit()
                await session.refresh(db_credit)
                return Credit(
                    credit_id=db_credit.credit_id,
                    user_id=db_credit.user_id,
                    amount=float(db_credit.amount),
                    transaction_id=db_credit.transaction_id,
                    expires_at=db_credit.expires_at,
                    created_at=db_credit.created_at,
                    updated_at=db_credit.updated_at,
                )
    
    async def get_credit_balance(self, user_id: str) -> Decimal:
        async with self.async_session() as session:
            from sqlalchemy import select, func
            from decimal import Decimal
            stmt = select(func.sum(CreditModel.amount)).where(CreditModel.user_id == user_id)
            result = await session.execute(stmt)
            balance = result.scalar() or Decimal("0")
            return balance
    
    async def deduct_credit(self, user_id: str, amount: Decimal) -> bool:
        async with self.async_session() as session:
            from sqlalchemy import select
            stmt = select(CreditModel).where(CreditModel.user_id == user_id)
            result = await session.execute(stmt)
            credit = result.scalar_one_or_none()
            if not credit:
                return False
            if credit.amount < amount:
                return False
            credit.amount -= amount
            credit.updated_at = datetime.now()
            await session.commit()
            return True
    
    async def create_transaction(self, transaction: Transaction) -> Transaction:
        async with self.async_session() as session:
            from decimal import Decimal
            db_txn = TransactionModel(
                transaction_id=transaction.transaction_id,
                user_id=transaction.user_id,
                org_id=transaction.org_id,
                order_id=transaction.order_id,
                provider=transaction.provider,
                provider_transaction_id=transaction.provider_transaction_id,
                amount=Decimal(str(transaction.amount)),
                currency=transaction.currency,
                status=transaction.status,
                extra_data=transaction.metadata,
                created_at=transaction.created_at,
            )
            session.add(db_txn)
            await session.commit()
            await session.refresh(db_txn)
            return Transaction(
                transaction_id=db_txn.transaction_id,
                user_id=db_txn.user_id,
                org_id=db_txn.org_id,
                order_id=db_txn.order_id,
                provider=db_txn.provider,
                provider_transaction_id=db_txn.provider_transaction_id,
                amount=float(db_txn.amount),
                currency=db_txn.currency,
                status=db_txn.status,
                metadata=db_txn.extra_data or {},
                created_at=db_txn.created_at,
            )
    
    async def get_orders_count_today(self, org_id: str) -> int:
        async with self.async_session() as session:
            from sqlalchemy import select, func
            from datetime import date
            today = date.today()
            stmt = select(func.count()).select_from(OrderModel).where(
                OrderModel.org_id == org_id,
                OrderModel.created_at >= datetime.combine(today, datetime.min.time()),
            )
            result = await session.execute(stmt)
            return result.scalar() or 0


class ConvexAdapter(DatabaseAdapter):
    """Convex adapter for production (stub - to be implemented)."""
    
    def __init__(self, convex_url: str, convex_token: str):
        self.convex_url = convex_url
        self.convex_token = convex_token
        logger.warning("ConvexAdapter is a stub - full implementation pending")
    
    async def create_user(self, user: User) -> User:
        # TODO: Implement Convex mutation
        raise NotImplementedError("ConvexAdapter.create_user not yet implemented")
    
    async def get_user(self, user_id: str) -> Optional[User]:
        # TODO: Implement Convex query
        raise NotImplementedError("ConvexAdapter.get_user not yet implemented")
    
    async def create_organization(self, org: Organization) -> Organization:
        raise NotImplementedError("ConvexAdapter.create_organization not yet implemented")
    
    async def get_organization(self, org_id: str) -> Optional[Organization]:
        raise NotImplementedError("ConvexAdapter.get_organization not yet implemented")
    
    async def get_organizations_by_user(self, user_id: str) -> List[Organization]:
        raise NotImplementedError("ConvexAdapter.get_organizations_by_user not yet implemented")
    
    async def update_organization(self, org_id: str, **updates) -> Optional[Organization]:
        raise NotImplementedError("ConvexAdapter.update_organization not yet implemented")
    
    async def create_order(self, order: Order) -> Order:
        raise NotImplementedError("ConvexAdapter.create_order not yet implemented")
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        raise NotImplementedError("ConvexAdapter.get_order not yet implemented")
    
    async def get_orders_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        raise NotImplementedError("ConvexAdapter.get_orders_by_user not yet implemented")
    
    async def update_order(self, order_id: str, **updates) -> Optional[Order]:
        raise NotImplementedError("ConvexAdapter.update_order not yet implemented")
    
    async def create_subscription(self, subscription: Subscription) -> Subscription:
        raise NotImplementedError("ConvexAdapter.create_subscription not yet implemented")
    
    async def get_subscription_by_org(self, org_id: str) -> Optional[Subscription]:
        raise NotImplementedError("ConvexAdapter.get_subscription_by_org not yet implemented")
    
    async def update_subscription(self, subscription_id: str, **updates) -> Optional[Subscription]:
        raise NotImplementedError("ConvexAdapter.update_subscription not yet implemented")
    
    async def create_credit(self, credit: Credit) -> Credit:
        raise NotImplementedError("ConvexAdapter.create_credit not yet implemented")
    
    async def get_credit_balance(self, user_id: str) -> Decimal:
        raise NotImplementedError("ConvexAdapter.get_credit_balance not yet implemented")
    
    async def deduct_credit(self, user_id: str, amount: Decimal) -> bool:
        raise NotImplementedError("ConvexAdapter.deduct_credit not yet implemented")
    
    async def create_transaction(self, transaction: Transaction) -> Transaction:
        raise NotImplementedError("ConvexAdapter.create_transaction not yet implemented")
    
    async def get_orders_count_today(self, org_id: str) -> int:
        raise NotImplementedError("ConvexAdapter.get_orders_count_today not yet implemented")


# Singleton database instance
_db_adapter: Optional[DatabaseAdapter] = None


def get_database() -> DatabaseAdapter:
    """Get database adapter instance (SQLite for local, Convex for production)."""
    global _db_adapter
    if _db_adapter is None:
        convex_url = os.getenv("CONVEX_URL", "")
        convex_token = os.getenv("CONVEX_TOKEN", "")
        
        if convex_url and convex_token:
            logger.info("Using Convex database adapter")
            _db_adapter = ConvexAdapter(convex_url, convex_token)
        else:
            database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./local.db")
            logger.info(f"Using SQLite database adapter: {database_url}")
            _db_adapter = SQLiteAdapter(database_url)
    
    return _db_adapter

