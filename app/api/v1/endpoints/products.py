from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate

router = APIRouter()

@router.post("/")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    new_product = Product(
        brand=product.brand,
        name=product.name,
        weight=product.weight,
        flavor=product.flavor,
        image=product.image,
        price=product.price,
        original_price=product.original_price,
        discount_percentage=product.discount_percentage,
        rating=product.rating,
        review_count=product.review_count,
        category=product.category,
        verified=product.verified,
        seller_name=product.seller_name,
        subscription_available=product.subscription_available,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product_id": new_product.id
    }

@router.get("/")
def get_products(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    verified: bool | None = Query(default=None),
    subscription: bool | None = Query(default=None),
    db: Session = Depends(get_db)
):

    query = db.query(Product)

    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.brand.ilike(f"%{search}%"),
                Product.flavor.ilike(f"%{search}%")
            )
        )

    if category:
        query = query.filter(
            Product.category.ilike(category)
        )

    if verified is not None:
        query = query.filter(
            Product.verified == verified
        )

    if subscription is not None:
        query = query.filter(
            Product.subscription_available == subscription
        )

    return query.all()

@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product