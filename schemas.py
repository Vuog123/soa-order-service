from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

OrderStatus = Literal["pending", "completed", "cancelled"]


class OrderItemInOrder(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: str = Field(min_length=1, max_length=255)
    items: list[OrderItemInOrder] = Field(default_factory=list)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int = Field(gt=0)
    product_name: Optional[str] = Field(default=None, max_length=255)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)


class OrderItemUpdate(BaseModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = Field(default=None, max_length=255)
    quantity: Optional[int] = Field(default=None, gt=0)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_email: str
    total_amount: Decimal
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: list[OrderItemResponse] = Field(default_factory=list)
