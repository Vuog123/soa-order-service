import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8002"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "order_service_db")

DATABASE_URL = (
    f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000").rstrip("/")
AUTH_VERIFY_PATH = os.getenv("AUTH_VERIFY_PATH", "/auth")
AUTH_VERIFY_METHOD = os.getenv("AUTH_VERIFY_METHOD", "GET").upper()

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001").rstrip("/")
PRODUCT_DETAIL_PATH = os.getenv("PRODUCT_DETAIL_PATH", "/products/{product_id}")
