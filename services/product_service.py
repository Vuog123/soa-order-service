from decimal import Decimal
from typing import Optional
import httpx
from fastapi import HTTPException, status

from config import PRODUCT_DETAIL_PATH, PRODUCT_SERVICE_URL


async def get_product_and_check_stock(
    product_id: int,
    quantity: int,
    authorization: Optional[str] = None,
) -> dict:
    """Gọi Product Service để lấy thông tin và kiểm tra tồn kho."""
    url = f"{PRODUCT_SERVICE_URL}{PRODUCT_DETAIL_PATH.format(product_id=product_id)}"
    headers = {"Authorization": authorization} if authorization else {}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể kết nối tới dịch vụ quản lý sản phẩm (Product Service)",
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sản phẩm có id={product_id}",
        )

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Lỗi khi truy vấn dịch vụ quản lý sản phẩm (status={response.status_code})",
        )

    raw_data = response.json()
    product = raw_data.get("data") or raw_data.get("product") or raw_data

    product_name = product.get("name") or product.get("product_name") or f"Product #{product_id}"
    raw_price = product.get("price") if product.get("price") is not None else product.get("unit_price")
    raw_stock = (
        product.get("stock")
        if product.get("stock") is not None
        else product.get("quantity")
        if product.get("quantity") is not None
        else product.get("stock_quantity")
    )

    if raw_price is None or raw_stock is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Dữ liệu trả về từ Product Service thiếu thông tin giá hoặc tồn kho",
        )

    stock = int(raw_stock)
    if stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sản phẩm '{product_name}' không đủ tồn kho (còn {stock}, yêu cầu {quantity})",
        )

    return {
        "product_id": product_id,
        "product_name": str(product_name),
        "unit_price": Decimal(str(raw_price)),
        "stock": stock,
    }
