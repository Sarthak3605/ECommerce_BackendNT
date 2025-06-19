from pydantic import BaseModel,Field

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0") #gt is greater than and ... is no default value and it is required to use

class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        orm_mode = True
