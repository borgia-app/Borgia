from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic.base import ContextMixin

from borgia.utils import is_association_manager
from shops.models import Shop, Product

DEFAULT_PERMISSIONS_CHIEFS = ['add_user', 'view_user', 'add_recharging',
                              'add_product', 'change_product', 'delete_product', 'view_product',
                              'change_price_product',
                              'view_sale', 'use_operatorsalemodule',
                              'add_stockentry', 'view_stockentry',
                              'add_inventory', 'view_inventory']
DEFAULT_PERMISSIONS_ASSOCIATES = ['add_user', 'view_user',
                                  'add_product', 'change_product', 'view_product',
                                  'view_sale', 'use_operatorsalemodule',
                                  'add_stockentry', 'view_stockentry',
                                  'add_inventory', 'view_inventory']

def is_shop_manager(shop, user):
    if user in shop.get_managers():
        return True
    else:
        return False

class ShopPermissionAndContextMixin(PermissionRequiredMixin, ContextMixin):
    """
    Mixin for Shop and Product views.
    For Permission :
    This mixin check if the user has the permission required. Then, it check if the user is a association manager.
    If the user is indeed an association manager, he can access forms for other shops.
    If the user is "only" a shop manager, he is restricted to his own shop and the related products.

    Also, add to context a few variable :
    - is_association_manager, bool
    - shop, Shop object
    """
    permission_required = None

    def __init__(self):
        self.shop = None

    def add_shop_object(self):
        try:
            self.shop = Shop.objects.get(pk=self.kwargs['shop_pk'])
        except ObjectDoesNotExist:
            raise Http404

    def add_context_objects(self):
        """
        Override to add more context objects for the view.
        """
        self.add_shop_object()

    def has_permission(self):
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            self.add_context_objects()

            if is_association_manager(self.request.user):
                self.is_association_manager = True
                return True
            else:
                self.is_association_manager = False
                return is_shop_manager(self.shop, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['is_association_manager'] = self.is_association_manager
        return context


class ProductPermissionAndContextMixin(ShopPermissionAndContextMixin):
    """
    Mixin for Product views.
    This mixin inherite from ShopPermissionAndContextMixin, and keep Permission verification.
    It only add the product context.
    """

    def __init__(self):
        self.product = None

    def add_product_object(self):
        try:
            self.product = Product.objects.get(pk=self.kwargs['product_pk'])
        except ObjectDoesNotExist:
            raise Http404

    def add_context_objects(self):
        super().add_context_objects()
        self.add_product_object()

    def has_permission(self):
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            return self.product.shop == self.shop

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context