"""Context processors để truyền cart_count vào tất cả templates."""
from .cart import get_or_create_cart


def cart_count(request):
    """Trả về số lượng sản phẩm trong giỏ hàng."""
    try:
        cart = get_or_create_cart(request)
        count = sum(item.quantity for item in cart.items.all())
        return {'cart_count': count}
    except Exception:
        return {'cart_count': 0}
