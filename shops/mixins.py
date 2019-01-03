from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic.base import ContextMixin

from borgia.utils import is_association_manager
from shops.models import Product, Shop
from shops.utils import is_shop_manager


class ShopMixin(LoginRequiredMixin, PermissionRequiredMixin, ContextMixin):
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
        self.is_association_manager = None

    def add_shop_object(self):
        """
        Define shop object.
        Raise Http404 is shop doesn't exist.
        """
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
        self.add_context_objects()
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
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


class ProductMixin(ShopMixin):
    """
    Mixin for Product views.
    This mixin inherite from ShopMixin, and keep Permission verification.
    It only add the product context.
    """

    def __init__(self):
        super().__init__()
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
