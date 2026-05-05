# Tài liệu mô tả yêu cầu phần mềm (SRS)

## Cây Cảnh Xanh - Website bán cây cảnh

---

## 1. Mục tiêu và phạm vi

**Mục tiêu**: Xây dựng website thương mại điện tử chuyên bán cây cảnh, sen đá, xương rồng.

**Phạm vi**:
- Người dùng: Duyệt sản phẩm, thêm giỏ hàng, đặt hàng
- Admin: Quản lý sản phẩm, danh mục, đơn hàng
- Không bao gồm: Thanh toán online (VNPay, Momo), đa ngôn ngữ

---

## 2. Nghiệp vụ và vai trò người dùng

| Vai trò | Mô tả | Quyền |
|---------|-------|-------|
| **Guest** | Khách chưa đăng nhập | Xem sản phẩm, thêm giỏ hàng (session) |
| **User** | Người dùng đã đăng ký | Guest + Đặt hàng, xem đơn hàng |
| **Admin** | Quản trị viên | CRUD sản phẩm, danh mục, quản lý đơn, dashboard |

---

## 3. Chức năng chính (tối thiểu 6)

1. **Duyệt sản phẩm**: Tìm kiếm, lọc theo danh mục/giá, sắp xếp
2. **Chi tiết sản phẩm**: Ảnh, mô tả, giá, thêm giỏ
3. **Giỏ hàng**: Thêm, sửa số lượng, xóa
4. **Đặt hàng**: Checkout với địa chỉ, số điện thoại
5. **Đăng nhập / Đăng ký**: Xác thực người dùng
6. **Quản trị**: CRUD sản phẩm, danh mục; Quản lý đơn hàng, cập nhật trạng thái
7. **Dashboard**: Thống kê, biểu đồ đơn hàng và danh mục

---

## 4. Use Case

- **Guest**: Xem sản phẩm, tìm kiếm, lọc, thêm giỏ, đăng nhập, đăng ký
- **User**: Tất cả Guest + Thanh toán, xem đơn hàng
- **Admin**: Tất cả User + Thêm/sửa/xóa sản phẩm, danh mục; Xem/cập nhật đơn hàng; Dashboard

---

## 5. ERD (≥5 thực thể)

- **User** (auth.User)
- **UserProfile** (1-1 User): role, phone, address
- **Category**: name, slug, description
- **Product** (n-1 Category): name, price, stock, image, status
- **Cart** (1-1 User hoặc session): 
- **CartItem** (n-1 Cart, n-1 Product): quantity
- **Order** (n-1 User): status, shipping_address, total_amount
- **OrderItem** (n-1 Order, n-1 Product): quantity, price, subtotal

---

## 6. Quan hệ dữ liệu

| Quan hệ | Mô tả |
|---------|-------|
| Category → Product | 1-n |
| User → Order | 1-n |
| Order → OrderItem | 1-n |
| Product → OrderItem | 1-n |
| User → Cart | 1-1 |
| Cart → CartItem | 1-n |
| Product → CartItem | 1-n |

---

## 7. Kiến trúc công nghệ

| Thành phần | Công nghệ |
|------------|-----------|
| Ngôn ngữ | Python |
| Framework | Django |
| CSDL | SQLite (dev) / PostgreSQL (production) |
| Frontend | Bootstrap 5, Chart.js |

---

## 8. Bảng dữ liệu, khóa

| Bảng | Khóa chính | Khóa ngoại |
|------|------------|------------|
| Category | id | - |
| Product | id | category_id |
| UserProfile | id | user_id |
| Cart | id | user_id |
| CartItem | id | cart_id, product_id |
| Order | id (UUID) | user_id |
| OrderItem | id | order_id, product_id |

---

## 9. Seed data

Chạy: `python manage.py seed_data`

Tạo: 4 danh mục, 7 sản phẩm, user admin (admin/admin123), user1 (user1/admin123).

---

## 10. Bảo mật cơ bản

- Mật khẩu: Django hash (PBKDF2)
- Input: Django form validation
- Upload ảnh: Validate format (jpg, png, webp), size (≤2MB)
- Cấu hình: .env (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
