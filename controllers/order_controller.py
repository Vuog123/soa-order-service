from collections import defaultdict
from decimal import Decimal
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from models import Order, OrderItem
from schemas import OrderCreate, OrderStatusUpdate
from services.product_service import get_product_and_check_stock


def get_all_orders(db: Session) -> list[Order]:
    return db.query(Order).options(joinedload(Order.items)).all()


def get_order_by_id(db: Session, order_id: int) -> Order:
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy đơn hàng có id={order_id}",
        )
    return order


async def create_order(
    db: Session,
    payload: OrderCreate,
    authorization: Optional[str] = None,
) -> Order:
    # Gom tổng số lượng theo product_id để kiểm tra tồn kho chính xác
    qty_by_product: dict[int, int] = defaultdict(int)
    for item in payload.items:
        qty_by_product[item.product_id] += item.quantity

    product_info_map: dict[int, dict] = {}
    for product_id, total_qty in qty_by_product.items():
        product_info_map[product_id] = await get_product_and_check_stock(
            product_id=product_id,
            quantity=total_qty,
            authorization=authorization,
        )

    order_items: list[OrderItem] = []
    total_amount = Decimal("0.00")

    for item in payload.items:
        info = product_info_map[item.product_id]
        unit_price: Decimal = info["unit_price"]
        total_price = unit_price * item.quantity
        total_amount += total_price

        order_items.append(
            OrderItem(
                product_id=item.product_id,
                product_name=info["product_name"],
                quantity=item.quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
        )

    new_order = Order(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        total_amount=total_amount,
        status="pending",
        items=order_items,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


def update_order_status(
    db: Session,
    order_id: int,
    payload: OrderStatusUpdate,
) -> Order:
    order = get_order_by_id(db, order_id)
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order_id: int) -> dict:
    order = get_order_by_id(db, order_id)
    db.delete(order)
    db.commit()
    return {"message": f"Đã xóa đơn hàng id={order_id}"}
