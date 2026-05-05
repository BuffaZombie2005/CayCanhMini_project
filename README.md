# Cây Cảnh Xanh - Website Bán Cây Cảnh (Django)

Website bán cây cảnh, sen đá, xương rồng xây dựng bằng Django.

## Tính năng chính

- **Trang chủ**: Sản phẩm nổi bật, danh mục
- **Sản phẩm**: Tìm kiếm, lọc theo danh mục/giá, sắp xếp
- **Giỏ hàng**: Thêm/sửa/xóa, hỗ trợ guest và user
- **Đặt hàng**: Checkout, theo dõi đơn hàng
- **Phân quyền**: Guest (xem), User (mua), Admin (quản trị)
- **Admin**: CRUD sản phẩm, danh mục, đơn hàng; Dashboard với biểu đồ Chart.js
- **Bảo mật**: .env, hash mật khẩu, validate input, validate upload ảnh (format, 2MB)

## Yêu cầu

- Python 3.10+
- Django 5+
- llama3.2 (AI)

## Cài đặt và chạy

```bash
# 1. Tạo môi trường ảo (nếu chưa có)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. File .env đã có sẵn (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
# Chỉnh SECRET_KEY nếu deploy production

# 4. Di chuyển vào thư mục mysite
cd mysite

# 5. Chạy migrations (đã chạy rồi thì bỏ qua)
python manage.py migrate

# 6. Tạo dữ liệu mẫu
python manage.py seed_data

# 7. Chạy server
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000/

## Tài khoản mẫu

| Vai trò | Username | Password |
|---------|----------|----------|
| Admin   | admin    | admin123 |
| User    | user1    | admin123 |

## Cấu trúc dự án

```
mysite/
├── manage.py
├── mysite/           # Project config
│   ├── settings.py
│   └── urls.py
├── shop/             # App chính
│   ├── models.py     # Category, Product, Order, Cart, UserProfile...
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── templates/shop/
│   └── management/commands/seed_data.py
├── media/            # Upload ảnh sản phẩm
└── db.sqlite3
```

## Tài liệu bổ sung

- [SRS.md](docs/SRS.md) - Mô tả yêu cầu phần mềm (SRS)
- [ERD.md](docs/ERD.md) - Sơ đồ ERD, Use Case

## Tiến độ

- [x] Cấu trúc Django chuẩn
- [x] Models: Category, Product, Cart, Order, UserProfile
- [x] CRUD sản phẩm, danh mục (Admin)
- [x] Tìm kiếm, lọc, sắp xếp sản phẩm
- [x] Giỏ hàng, đặt hàng, trạng thái đơn
- [x] Đăng nhập, đăng ký, phân quyền
- [x] Upload ảnh + validate (format, size)
- [x] Dashboard Chart.js
- [x] .env, template inheritance, toast messages
