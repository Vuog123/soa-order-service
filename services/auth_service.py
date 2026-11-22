from typing import Optional
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import AUTH_SERVICE_URL, AUTH_VERIFY_METHOD, AUTH_VERIFY_PATH

security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """Xác thực Bearer token thông qua Auth Service."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu token xác thực (Authorization: Bearer <token>)",
        )

    auth_header = f"{credentials.scheme} {credentials.credentials}"
    verify_url = f"{AUTH_SERVICE_URL}{AUTH_VERIFY_PATH}"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.request(
                method=AUTH_VERIFY_METHOD,
                url=verify_url,
                headers={"Authorization": auth_header},
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Không thể kết nối tới dịch vụ xác thực (Auth Service)",
        )

    if response.status_code != status.HTTP_200_OK:
        try:
            detail = response.json().get("detail", "Token không hợp lệ hoặc đã hết hạn")
        except ValueError:
            detail = "Token không hợp lệ hoặc đã hết hạn"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    try:
        body = response.json()
        user_data = body.get("data", body) if isinstance(body, dict) else {"authenticated": True}
    except ValueError:
        user_data = {"authenticated": True}

    return {"user": user_data, "authorization": auth_header}
