from sqlalchemy import Column, Integer, String, Float, Boolean

from app.core.database import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    brand = Column(String, nullable=False)

    name = Column(String, nullable=False)

    weight = Column(String)

    flavor = Column(String)

    image = Column(String)

    price = Column(Integer)

    original_price = Column(Integer)

    discount_percentage = Column(Integer)

    rating = Column(Float)

    review_count = Column(Integer)

    category = Column(String)

    verified = Column(Boolean, default=False)

    seller_name = Column(String)

    subscription_available = Column(Boolean, default=False)

    stock = Column(Integer)