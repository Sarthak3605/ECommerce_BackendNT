from sqlalchemy import Column, Integer, ForeignKey, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum

class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("OrderItem", back_populates="order") #in backpopulate changes on one reflects on other as well OrderItem is the second in the one to many relationship and order is how they connected

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id",ondelete="SET NULL"),nullable=True)
    quantity = Column(Integer)
    price_at_purchase = Column(Float)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
