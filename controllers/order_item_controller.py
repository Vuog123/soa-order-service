from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Order, OrderItem
from schemas import OrderItemCreate, OrderItemUpdate
from services.product_service import get_product_and_check_stock


def _recalculate_order_total(db: Session, order: Order) -> None:
    total = (
        db.query(func.coalesce(func.sum(OrderItem.total_price), 0))
        .filter(OrderItem.order_id == order.id)
        .scalar()
    )
    order.total_amount = Decimal(str(total))


def get_all_order_items(db: Session) -> list[OrderItem]:
    return db.query(OrderItem).all()


def get_order_item_by_id(db: Session, item_id: int) -> OrderItem:
    item = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy chi tiết đơn hàng có id={item_id}",
        )
    return item


async def create_order_item(
    db: Session,
    payload: OrderItemCreate,
    authorization: Optional[str] = None,
) -> OrderItem:
    order = db.query(Order).filter(Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đơn hàng có id={payload.order_id}",
        )

    product_info = await get_product_and_check_stock(
        product_id=payload.product_id,
        quantity=payload.quantity,
        authorization=authorization,
    )

    product_name = payload.product_name or product_info["product_name"]
    unit_price = (
        payload.unit_price
        if payload.unit_price is not None
        else product_info["unit_price"]
    )
    total_price = unit_price * payload.quantity

    new_item = OrderItem(
        order_id=payload.order_id,
        product_id=payload.product_id,
        product_name=product_name,
        quantity=payload.quantity,
        unit_price=unit_price,
        total_price=total_price,
    )
    db.add(new_item)
    db.flush()

    _recalculate_order_total(db, order)
    db.commit()
    db.refresh(new_item)
    return new_item


async def update_order_item(
    db: Session,
    item_id: int,
    payload: OrderItemUpdate,
    authorization: Optional[str] = None,
) -> OrderItem:
    item = get_order_item_by_id(db, item_id)
    order = db.query(Order).filter(Order.id == item.order_id).first()

    new_product_id = payload.product_id if payload.product_id is not None else item.product_id
    new_quantity = payload.quantity if payload.quantity is not None else item.quantity

    if payload.product_id is not None or payload.quantity is not None:
        product_info = await get_product_and_check_stock(
            product_id=new_product_id,
            quantity=new_quantity,
            authorization=authorization,
        )
        if payload.product_id is not None:
            item.product_id = new_product_id
            if payload.product_name is None:
                item.product_name = product_info["product_name"]
            if payload.unit_price is None:
                item.unit_price = product_info["unit_price"]

    if payload.product_name is not None:
        item.product_name = payload.product_name
    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.unit_price is not None:
        item.unit_price = payload.unit_price

    item.total_price = Decimal(str(item.unit_price)) * item.quantity
    db.flush()

    if order:
        _recalculate_order_total(db, order)

    db.commit()
    db.refresh(item)
    return item


def delete_order_item(db: Session, item_id: int) -> dict:
    item = get_order_item_by_id(db, item_id)
    order = db.query(Order).filter(Order.id == item.order_id).first()

    db.delete(item)
    db.flush()

    if order:
        _recalculate_order_total(db, order)

    db.commit()
    return {"message": f"Đã xóa mặt hàng id={item_id} khỏi đơn hàng"}
