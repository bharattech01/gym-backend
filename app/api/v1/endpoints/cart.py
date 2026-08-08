from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.cart import Cart
from app.models.product import Product
from app.core.security import get_current_user


from app.schemas.cart import CartCreate

router = APIRouter()
@router.post("/add")
def add_to_cart(
    cart: CartCreate,
    payload=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_id = payload["user_id"]

    product = db.query(Product).filter(
        Product.id == cart.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing = db.query(Cart).filter(
        Cart.user_id == user_id,
        Cart.product_id == cart.product_id
    ).first()

    if existing:
        existing.quantity += cart.quantity
        db.commit()

        return {
            "message": "Quantity updated"
        }

    item = Cart(
        user_id=user_id,
        product_id=cart.product_id,
        quantity=cart.quantity
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return {
        "message": "Added to cart",
        "cart_id": item.id
    }


@router.get("/")
def get_cart(
    payload=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_id = payload["user_id"]

    cart_items = (
        db.query(Cart)
        .join(Product)
        .filter(Cart.user_id == user_id)
        .all()
    )

    return cart_items

@router.patch("/{cart_id}")
def update_quantity(
    cart_id: int,
    quantity: int,
    payload=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_id = payload["user_id"]

    item = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == user_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    item.quantity = quantity

    db.commit()

    return {
        "message": "Quantity updated"
    }

@router.delete("/{cart_id}")
def remove_item(
    cart_id: int,
    payload=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_id = payload["user_id"]

    item = db.query(Cart).filter(
        Cart.id == cart_id,
        Cart.user_id == user_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Removed successfully"
    }

@router.delete("/clear")
def clear_cart(
    payload=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_id = payload["user_id"]

    db.query(Cart).filter(
        Cart.user_id == user_id
    ).delete()

    db.commit()

    return {
        "message": "Cart cleared"
    }