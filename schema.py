from pydantic import BaseModel
import datetime

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    price: float



class SalesResponse(BaseModel):
    id: int
    date: datetime.date
    time: datetime.time
    product_id: int
    amount: int
    total_price:float

    class Config:
        from_attributes = True
    
class SalesCreate(BaseModel):
    date: datetime.date
    time: datetime.time
    product_id: int
    amount: int



class CartResponse(BaseModel):
    id: int
    creation_date: datetime.date
    state: str

    class Config:
        from_attributes = True
        
class CartCreate(BaseModel):
    creation_date: datetime.date
    state: str