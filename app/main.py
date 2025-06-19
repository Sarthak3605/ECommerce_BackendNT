from fastapi import FastAPI,Request
from app.core.database import Base,engine
from app.auth.models import Base as AuthBase
from app.products.models import Base as ProductBase
from app.cart.models import Base as CartBase
from app.orders.models import Base as OrderBase
from app.core.logging_utils import logger
from app.core.error_handler import register_exception_handlers

from app.auth.routes import router as auth_routes
from app.products.routes import router as product_routes
from app.cart.routes import router as cart_routes
from app.checkout.routes import router as checkout_routes
from app.orders.routes import router as order_routes

app = FastAPI(title="E-Commerce Backend Python")

# Create all tables for models
AuthBase.metadata.create_all(bind=engine)
ProductBase.metadata.create_all(bind=engine)
CartBase.metadata.create_all(bind=engine)
OrderBase.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Log each API request (IP, method, path)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_ip = request.client.host #ip address
    method = request.method #Http methods
    path = request.url.path #request paths like (/auth,/order...etc)
    logger.info(f"API Access - IP: {client_ip}, Method: {method}, Path: {path}")
    response = await call_next(request)
    return response

register_exception_handlers(app)

# Include routers for diffrent routes
app.include_router(auth_routes)
app.include_router(product_routes)
app.include_router(cart_routes)
app.include_router(checkout_routes)
app.include_router(order_routes)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!!"}