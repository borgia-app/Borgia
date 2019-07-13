from django.apps import AppConfig


class ShopConfig(AppConfig):
    name = 'shops'

    def ready(self):
        # Import shop signals
        from shops.signals import create_shop_groups
