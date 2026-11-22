from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from controllers import order_item_controller
from database import get_db
from schemas import OrderItemCreate, OrderItemResponse, OrderItemUpdate
from services.auth_service import verify_token

router = APIRouter(prefix="/order_items", tags=["Order Items"])


@router.get("", response_model=list[OrderItemResponse])
def get_order_items(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return order_item_controller.get_all_order_items(db)


@router.get("/{item_id}", response_model=OrderItemResponse)
def get_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return order_item_controller.get_order_item_by_id(db, item_id)


@router.post("", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
async def create_order_item(
    payload: OrderItemCreate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_token),
):
    return await order_item_controller.create_order_item(db, payload, auth["authorization"])


@router.put("/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    item_id: int,
    payload: OrderItemUpdate,
    db: Session = Depends(get_db),
    auth: dict = Depends(verify_token),
):
    return await order_item_controller.update_order_item(db, item_id, payload, auth["authorization"])


@router.delete("/{item_id}")
def delete_order_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    return order_item_controller.delete_order_item(db, item_id)
