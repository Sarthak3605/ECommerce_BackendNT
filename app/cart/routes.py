from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.cart import models, schemas
from app.auth.routes import get_current_user
from app.products.models import Product

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_db(): #opens and closes db for each request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.CartItemOut)
def add_to_cart(item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    #no negative quantity
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    #quantity of item to add should be greater than stock
    if item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock} items available in stock"
        )

    cart_item = db.query(models.CartItem).filter_by(user_id=current_user.id, product_id=item.product_id).first() #fetch item in cart

    if cart_item:
        new_quantity = cart_item.quantity + item.quantity
        if new_quantity > product.stock:
             raise HTTPException(
                status_code=400,
                detail=f"Only {product.stock} items available in stock. You already have {cart_item.quantity} in cart."
            )
        cart_item.quantity = new_quantity
    else:
        cart_item = models.CartItem(user_id=current_user.id, product_id=item.product_id, quantity=item.quantity)
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.get("/", response_model=list[schemas.CartItemOut])
def view_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            item.product_name = "This product has been removed by admin"
        else:
            item.product_name = product.name

    return cart_items

@router.put("/{product_id}", response_model=schemas.CartItemOut)
def update_cart(product_id: int, item: schemas.CartItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    #quantity should not be negative
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    product = db.query(Product).filter(Product.id == product_id).first() #filter the product to find first if exists

    if not product:
        raise HTTPException(status_code=400, detail="Product not found!!")

    if item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product.stock} items available in stock"
        )

    cart_item = db.query(models.CartItem).filter_by(user_id=current_user.id, product_id=product_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.quantity = item.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/{product_id}")
def remove_from_cart(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cart_item = db.query(models.CartItem).filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}
