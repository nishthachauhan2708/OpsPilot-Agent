import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    orders = relationship("Order", back_populates="customer")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)

    orders = relationship("Order", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    amount = Column(Float, nullable=False)
    order_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    expected_delivery = Column(DateTime, nullable=False)
    actual_delivery = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False)  # processing, shipped, delivered, delayed, cancelled
    tracking_status = Column(String(200), nullable=False)

    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    returns = relationship("Return", back_populates="order")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True)
    stock = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)

    product = relationship("Product", back_populates="inventory")

class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, default="pending")  # pending, approved, rejected, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="returns")

class ActionRequest(Base):
    __tablename__ = "action_requests"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(50), nullable=False)  # e.g., create_return_request, update_order
    payload = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(50), nullable=False, index=True)
    tool_name = Column(String(50), nullable=False)
    input_summary = Column(Text, nullable=False)
    output_summary = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="success")  # success, error, pending_approval
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
