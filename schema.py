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


class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    amount: int

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    creation_date: datetime.date
    state: str
    items: list[CartItemResponse] = []
    
    class Config:
        from_attributes = True
        
class CartCreate(BaseModel):
    creation_date: datetime.date
    state: str

class CartProductCreate(BaseModel):
    product_id: int
    amount: int


# Lo que el cliente envía al crear una venta (nunca incluye total_price)
class SalesCreate(BaseModel):
    date: datetime.date
    time: datetime.time
    cart_id: int


# Lo que el cliente envía al actualizar una venta: solo fecha y hora
class SalesUpdate(BaseModel):
    date: datetime.date
    time: datetime.time


# Lo que el cliente envía para asignar un carrito a una venta existente
class SalesCartAssign(BaseModel):
    cart_id: int


# Lo que la API devuelve: la venta con su total y el carrito completo adentro
class SalesResponse(BaseModel):
    id: int
    date: datetime.date
    time: datetime.time
    total_price: float
    cart: CartResponse

    class Config:
        from_attributes = True