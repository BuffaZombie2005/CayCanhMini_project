"""Logic giỏ hàng - hỗ trợ cả user đăng nhập và guest (session)."""
from .models import Cart


def get_or_create_cart(request):
    """Lấy hoặc tạo giỏ hàng cho user/session hiện tại."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, defaults={})
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(
            session_key=session_key, defaults={'user': None}
        )
    return cart
