from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import SessionLocal
from app.auth.routes import get_current_user
from app.core.logging_utils import logger
from app.orders import models, schemas
from app.products.models import Product

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.OrderOut])
def get_user_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    orders = db.query(models.Order)\
        .options(joinedload(models.Order.items))\
        .filter(models.Order.user_id == current_user.id)\
        .order_by(models.Order.created_at.desc())\
        .all()

        # adding names to the item
    for order in orders:
        for item in order.items:
            if item.product_id:
               product = db.query(Product).filter(Product.id == item.product_id).first()
               item.product_name = product.name if product else "Product not found!!!"
            else:
                item.product_name = "Product not found!!!"

    logger.info(f"Order history viewed by: {current_user.email}")
    return orders

@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order_detail(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(models.Order)\
        .options(joinedload(models.Order.items))\
        .filter(models.Order.id == order_id, models.Order.user_id == current_user.id)\
        .first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            item.product_name = product.name if product else "Product not found!!!"
    logger.info(f"Order detail viewed - order_id: {order_id}, user: {current_user.email}")
    return order
