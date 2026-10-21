from pydantic import BaseModel

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    price: float

    class Config:
            from_attributes = True