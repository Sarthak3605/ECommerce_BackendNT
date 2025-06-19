from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth.models import User,UserRole
from app.core.database import SessionLocal
from app.products import models, schemas
from app.cart.models import CartItem
from app.core.logging_utils import logger
from app.auth.routes import get_current_user, require_admin

router = APIRouter(tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(user: User = Depends(get_current_user)):
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.post("/admin/products", response_model=schemas.ProductOut) #creation of new product by admin
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product created: {product.name} by Admin")
    return db_product

@router.get("/admin/products", response_model=list[schemas.ProductOut]) #fetch all the products
def list_all_products_admin(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.Product).all()

@router.get("/admin/products/{id}", response_model=schemas.ProductOut) #get the product by it's id for admin only
def get_product_admin(id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/admin/products/{id}", response_model=schemas.ProductOut)
def update_product(id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in data.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    logger.info(f"{product.name} updated: ID {id}")
    return product

@router.delete("/admin/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.query(CartItem).filter(CartItem.product_id == id).delete() # delete the product from all the carts

    db.delete(product) #delete the product from database
    db.commit()
    logger.info(f"Cart delete - user: {admin.email}, product_id: {id}")
    return {"message": f"{product.name} deleted from all carts."}

#Public routes or User routes
@router.get("/products", response_model=list[schemas.ProductOut])
def public_product_listing(
    db: Session = Depends(get_db), #parameters to list the products
    category: str | None = None,
    min_price: float = 0,
    max_price: float = 1e6,
    sort_by: str = Query("price", enum=["price", "name"]),
    page: int = 1,
    page_size: int = 10,
):
    query = db.query(models.Product).filter(models.Product.price >= min_price, models.Product.price <= max_price)
    if category:
        query = query.filter(models.Product.category == category)
    if sort_by == "price":
        query = query.order_by(models.Product.price)
    elif sort_by == "name":
        query = query.order_by(models.Product.name)
    products = query.offset((page - 1) * page_size).limit(page_size).all()
    return products

@router.get("/products/search", response_model=list[schemas.ProductOut])
def search_products(keyword: str, db: Session = Depends(get_db)):
    return db.query(models.Product).filter(models.Product.name.ilike(f"%{keyword}%")).all()

@router.get("/products/{id}", response_model=schemas.ProductOut)
def get_product_details(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
