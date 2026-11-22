from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from controllers import order_controller
from database import get_db
from schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from services.auth_service import verify_token

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return order_controller.get_all_orders(db)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return order_controller.get_order_by_id(db, order_id)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_token),
):
    return await order_controller.create_order(db, payload, auth["authorization"])


@router.put("/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return order_controller.update_order_status(db, order_id, payload)


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return order_controller.delete_order(db, order_id)
