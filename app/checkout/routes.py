from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.auth.routes import get_current_user
from app.core.logging_utils import logger
from app.cart.models import CartItem
from app.products.models import Product
from app.orders.models import Order, OrderItem
from app.orders.schemas import OrderOut, CheckoutRequest,PaymentMethod

router = APIRouter(prefix="/checkout", tags=["Checkout"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=OrderOut) #this returns the newly created order as OrderOut
def checkout(data:CheckoutRequest, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all() #get all cart items

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0
    order_items = []

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product.name}'")

        product.stock -= item.quantity #update the stock
        subtotal = product.price * item.quantity #update the price product's price * total number of items
        total_amount += subtotal #total new amount to paid

        order_item = OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=product.price
        )
        order_item.product_name = product.name #optional but good ro add name
        order_items.append(order_item)
     #here we set the status based on payment
        order_status = "paid" if data.payment_method == PaymentMethod.online else "pending"
    # Create order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status=order_status,
        items=order_items
    )

    db.add(new_order)
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete() #after add we empty the cart
    db.commit()
    db.refresh(new_order)


    for item in new_order.items:
        item.product_name = item.product.name if item.product else "Product Unavailable!!"

    logger.info(f"Checkout - user: {current_user.email}, total: {total_amount}, payment: {data.payment_method}")
    logger.info(f"Order created - order_id: {new_order.id}, user: {current_user.email}")
    return new_order
