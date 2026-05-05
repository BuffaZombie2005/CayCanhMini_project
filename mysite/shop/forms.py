"""
Forms với validation - đăng ký, đăng nhập, sản phẩm (file upload với validate format + size).
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Product, Category, Order

# Giới hạn upload: 2MB, định dạng: jpg, jpeg, png, webp
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB


def validate_image(file):
    """Validate format và size của ảnh."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise forms.ValidationError(
            'Định dạng không hợp lệ. Chỉ chấp nhận: JPG, PNG, WebP.'
        )
    if file.size > MAX_IMAGE_SIZE:
        raise forms.ValidationError(
            f'Kích thước ảnh tối đa 2MB. Ảnh của bạn: {file.size // 1024}KB'
        )


class RegisterForm(UserCreationForm):
    """Form đăng ký - Django đã hash password tự động."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Tên đăng nhập này đã được sử dụng.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email này đã được đăng ký.')
        return email


class ProductForm(forms.ModelForm):
    """Form CRUD sản phẩm với validate ảnh upload."""

    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'stock', 'image', 'image_url', 'category', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png,image/webp'}),
            'image_url': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'https://... — URL dài (signed/CDN) được hỗ trợ; để trống nếu chỉ upload file',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validate_image(image)
        return image

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Giá phải >= 0.')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('Số lượng phải >= 0.')
        return stock


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class CheckoutForm(forms.Form):
    """Form đặt hàng."""
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Địa chỉ giao hàng', 'class': 'form-control'}),
        max_length=500
    )
    shipping_phone = forms.CharField(max_length=20, label='Số điện thoại', widget=forms.TextInput(attrs={'class': 'form-control'}))
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ghi chú (không bắt buộc)', 'class': 'form-control'})
    )

    def clean_shipping_phone(self):
        phone = self.cleaned_data.get('shipping_phone')
        if not phone or not phone.strip():
            raise forms.ValidationError('Vui lòng nhập số điện thoại.')
        return phone.strip()


class OrderStatusForm(forms.ModelForm):
    """Form cập nhật trạng thái đơn hàng (Admin)."""
    class Meta:
        model = Order
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': 'form-select'})}
