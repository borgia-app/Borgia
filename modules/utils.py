from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import ContextMixin

from modules.models import OperatorSaleModule, SelfSaleModule
from shops.models import Shop


class ShopModulePermissionAndContextMixin(PermissionRequiredMixin, ContextMixin):
    """
    Mixin for Module Shop views.
    For Permission :

    Also, add to context a few variable :
    - shop, Shop object
    - module, a ShopModule object
    """
    permission_required = None

    def __init__(self):
        self.shop = None
        self.module = None

    def add_shop_object(self):
        try:
            self.shop = Shop.objects.get(pk=self.kwargs['shop_pk'])
        except ObjectDoesNotExist:
            raise Http404

    def add_module_object(self):
        module_class = self.kwargs['module_class']
        if module_class == "self_sales":
            self.module = SelfSaleModule.objects.get_or_create(
                shop=self.shop)[0]
        elif module_class == "operator_sales":
            self.module = OperatorSaleModule.objects.get_or_create(
                shop=self.shop)[0]
        else:
            raise Http404

    def has_permission(self):
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            self.add_shop_object()
            self.add_module_object()
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['module'] = self.module
        return context
