# Sơ đồ ERD và Use Case

## ERD (Entity-Relationship Diagram)

```
┌─────────────┐       ┌──────────────┐
│    User     │───1:1─│ UserProfile  │
└──────┬──────┘       └──────────────┘
       │
       │ 1:n
       ▼
┌─────────────┐       ┌─────────────┐
│   Order     │───1:n─│ OrderItem   │
└─────────────┘       └──────┬──────┘
       │                     │ n:1
       │ 1:n                 ▼
       │              ┌─────────────┐
       │              │   Product   │
       │              └──────┬──────┘
       │                     │ n:1
       │                     ▼
       │              ┌─────────────┐
       │              │  Category   │
       └──────────────└─────────────┘

┌─────────────┐       ┌─────────────┐
│    Cart     │───1:n─│  CartItem   │────n:1────┐
└──────┬──────┘       └─────────────┘           │
       │ 1:1                                     │
       │ (hoặc session)                          │
       ▼                                         ▼
┌─────────────┐                            ┌─────────────┐
│    User     │                            │   Product   │
└─────────────┘                            └─────────────┘
```

## Use Case Diagram (mô tả)

### Guest
- Xem trang chủ
- Xem danh sách sản phẩm
- Tìm kiếm, lọc, sắp xếp sản phẩm
- Xem chi tiết sản phẩm
- Thêm sản phẩm vào giỏ hàng
- Đăng nhập
- Đăng ký

### User (đã đăng nhập)
- Tất cả Use Case của Guest
- Xem giỏ hàng, cập nhật giỏ
- Đặt hàng (checkout)
- Xem danh sách đơn hàng
- Xem chi tiết đơn hàng

### Admin
- Tất cả Use Case của User
- Dashboard thống kê
- CRUD danh mục
- CRUD sản phẩm (upload ảnh)
- Xem danh sách đơn hàng
- Cập nhật trạng thái đơn hàng
