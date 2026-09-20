from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    role = Column(String(50), default="customer")  # customer, admin, manager
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(50), default="pending")  # pending, completed, cancelled, shipped
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    payment_method = Column(String(50), nullable=False)  # credit_card, paypal, upi, bank_transfer
    status = Column(String(50), default="successful")  # successful, failed, pending
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="payments")
