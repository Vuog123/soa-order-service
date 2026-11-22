from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from config import APP_HOST, APP_PORT
from database import Base, engine
from routes.order_item_routes import router as order_item_router
from routes.order_routes import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Order Management Service",
    description="Dịch vụ quản lý đơn hàng - Bài thực hành số 4 (SOA)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(order_router)
app.include_router(order_item_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
