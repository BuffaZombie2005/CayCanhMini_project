from django.apps import AppConfig


class ShopConfig(AppConfig):
    name = 'shop'
    verbose_name = 'Cửa hàng cây cảnh'

    def ready(self):
        import shop.signals  # noqa: F401
