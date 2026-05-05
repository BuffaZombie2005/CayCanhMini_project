"""
Models cho website bán cây cảnh.
ERD: User -> Order (1-n), Order -> OrderItem (1-n), Product -> OrderItem (1-n),
     Category -> Product (1-n), User -> Cart (1-1), Cart -> CartItem (1-n), Product -> CartItem (1-n)
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid


class Category(models.Model):
    """Danh mục cây cảnh (VD: Cây nội thất, Sen đá, Xương rồng)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Danh mục'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Sản phẩm cây cảnh"""
    STATUS_CHOICES = [
        ('active', 'Đang bán'),
        ('draft', 'Nháp'),
        ('inactive', 'Ngừng bán'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.TextField(blank=True, verbose_name='URL ảnh (từ mạng)')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sản phẩm'

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0

    def get_image_url(self):
        """Trả về URL ảnh: ưu tiên ảnh upload, không có thì dùng image_url."""
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None


class UserProfile(models.Model):
    """Profile mở rộng cho User - quản lý vai trò Guest/User/Admin"""
    ROLE_CHOICES = [
        ('guest', 'Khách'),
        ('user', 'Người dùng'),
        ('admin', 'Quản trị viên'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff

    def is_customer(self):
        return self.role in ('user', 'guest')


class Cart(models.Model):
    """Giỏ hàng - 1 user có 1 giỏ hàng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.pk}"

    def get_total(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """Mục trong giỏ hàng"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Đơn hàng - có trạng thái pending/confirmed/shipped/delivered/cancelled"""
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('confirmed', 'Đã xác nhận'),
        ('shipped', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã hủy'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    shipping_phone = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {str(self.id)[:8]} - {self.user.username}"


class OrderItem(models.Model):
    """Chi tiết từng sản phẩm trong đơn hàng"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
