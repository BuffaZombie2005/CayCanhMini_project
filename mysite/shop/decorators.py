"""Decorators cho phân quyền (Admin only, Login required)."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Chỉ Admin mới truy cập được."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Vui lòng đăng nhập.')
            return redirect('shop:login')
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_admin():
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('shop:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


def login_required_customer(view_func):
    """Chỉ User đăng nhập mới đặt hàng / xem đơn."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Vui lòng đăng nhập để thực hiện chức năng này.')
            return redirect('shop:login')
        return view_func(request, *args, **kwargs)
    return _wrapped
