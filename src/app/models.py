from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean, text, UniqueConstraint


class App_user(Base):
    __tablename__ = "app_user"

    id = Column(String(255), primary_key=True, nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))


class Subscription(Base):
    __tablename__ = "subscription"

    id = Column(String(255), primary_key=True, nullable=False)
    userId = Column(String(255), ForeignKey('app_user.id'), nullable=False)
    planId = Column(String(255), nullable=False)
    paymentMethod = Column(String(255), nullable=False)
    startDate = Column(TIMESTAMP(timezone=True), nullable=False)
    endDate = Column(TIMESTAMP(timezone=True), nullable=False)
    __table_args__ = (
        UniqueConstraint('userId', 'planId',
                         name='unique_user_plan_constraint'),
    )
