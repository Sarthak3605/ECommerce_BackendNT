from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"

class OrderItemBase(BaseModel):
    product_id: Optional[int]
    quantity: int
    price_at_purchase: float

class OrderItemOut(OrderItemBase):
    id: int
    product_name: str
    class Config:
        from_attributes = True
        extra = "allow"
#for checkout
class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

class PaymentMethod(str, Enum):
    cod = "COD",
    online = "Online"

class CheckoutRequest(BaseModel):
    payment_method: PaymentMethod

    class Config:
        from_attributes = True