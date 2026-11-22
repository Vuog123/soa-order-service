# Order Management Service (Bài thực hành số 4)

Dịch vụ quản lý đơn hàng độc lập theo kiến trúc SOA, chạy trên cổng riêng (`localhost:8002`) với cơ sở dữ liệu MySQL riêng (`order_service_db`).

## Cấu trúc thư mục

```text
order-service/
├── .env                  # Cấu hình cổng, MySQL, Auth Service, Product Service
├── .env.example          # File mẫu cấu hình
├── init_db.sql           # Script tạo CSDL và 2 bảng orders, order_items
├── requirements.txt      # Các thư viện Python cần thiết
├── config.py             # Đọc biến môi trường từ .env
├── database.py           # Kết nối MySQL qua SQLAlchemy
├── models.py             # Định nghĩa ORM cho bảng orders và order_items
├── schemas.py            # Validate dữ liệu request/response
├── services/
│   ├── auth_service.py   # Xác thực token qua Auth Service (Bài 2)
│   └── product_service.py# Kiểm tra tồn kho qua Product Service (Bài 3)
├── controllers/
│   ├── order_controller.py
│   └── order_item_controller.py
├── routes/
│   ├── order_routes.py
│   └── order_item_routes.py
└── main.py               # Khởi chạy ứng dụng FastAPI
```

## Cài đặt & Chạy

1. **Tạo cơ sở dữ liệu MySQL:**
   Chạy file `init_db.sql` trên MySQL (MySQL Workbench / CLI):
   ```bash
   mysql -u root -p < init_db.sql
   ```
   *(Lưu ý: Phụ lục đề bài ghi nhầm tiêu đề bảng là `other_items`, ở đây đặt chuẩn là `order_items` cho đồng bộ với API `/order_items`.)*

2. **Cấu hình `.env`:**
   Chỉnh thông tin kết nối MySQL và URL/endpoint của **Auth Service (Bài 2)** và **Product Service (Bài 3)** trong file `.env`:
   ```env
   APP_PORT=8002
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=order_service_db

   AUTH_SERVICE_URL=http://localhost:8000
   AUTH_VERIFY_PATH=/auth
   AUTH_VERIFY_METHOD=GET

   PRODUCT_SERVICE_URL=http://localhost:8001
   PRODUCT_DETAIL_PATH=/products/{product_id}
   ```

3. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Chạy service:**
   ```bash
   python main.py
   ```
   - Service chạy tại: `http://localhost:8002`
   - Tài liệu Swagger để test API: `http://localhost:8002/docs`

## Danh sách API

Tất cả các API đều yêu cầu header xác thực: `Authorization: Bearer <token>` (kiểm tra qua Auth Service).

### Đơn hàng (`/orders`)
- `GET /orders` — Lấy danh sách tất cả đơn hàng
- `GET /orders/{id}` — Lấy chi tiết một đơn hàng
- `POST /orders` — Tạo đơn hàng mới (có kiểm tra tồn kho từ Product Service)
  ```json
  {
    "customer_name": "Nguyen Van A",
    "customer_email": "a@example.com",
    "items": [
      { "product_id": 1, "quantity": 2 }
    ]
  }
  ```
- `PUT /orders/{id}` — Cập nhật trạng thái đơn hàng (`pending`, `completed`, `cancelled`)
  ```json
  {
    "status": "completed"
  }
  ```
- `DELETE /orders/{id}` — Xóa một đơn hàng

### Chi tiết đơn hàng (`/order_items`)
- `GET /order_items` — Lấy danh sách tất cả mặt hàng trong đơn hàng
- `GET /order_items/{id}` — Lấy thông tin chi tiết một mặt hàng
- `POST /order_items` — Tạo mặt hàng mới (tự kiểm tra tồn kho & cập nhật lại `total_amount` của đơn hàng)
  ```json
  {
    "order_id": 1,
    "product_id": 2,
    "quantity": 1
  }
  ```
- `PUT /order_items/{id}` — Cập nhật mặt hàng (cập nhật lại `total_price` và `total_amount`)
- `DELETE /order_items/{id}` — Xóa mặt hàng khỏi đơn hàng (cập nhật lại `total_amount`)
