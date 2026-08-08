from pydantic import BaseModel


class ProductCreate(BaseModel):

    brand: str

    name: str

    weight: str

    flavor: str

    image: str

    price: int

    original_price: int

    discount_percentage: int

    rating: float

    review_count: int

    category: str

    verified: bool

    seller_name: str

    subscription_available: bool

    stock: int