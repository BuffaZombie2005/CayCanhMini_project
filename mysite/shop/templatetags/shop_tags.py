"""Template tags cho shop."""
from django import template

register = template.Library()


@register.filter
def is_admin(user):
    """Kiểm tra user có phải admin không (staff hoặc role=admin)."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    try:
        return user.profile.role == 'admin'
    except Exception:
        return False
