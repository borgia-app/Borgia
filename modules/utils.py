from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import ContextMixin

from modules.models import OperatorSaleModule, SelfSaleModule
from shops.models import Shop


class ShopModuleMixin(object):
    def __init__(self):
        self.kwargs = None
        self.module_class = None
        self.shop = None
        self.module = None
        self.success_url = None

    def dispatch(self, request, *args, **kwargs):
        """
        Add self.module and modify success_url to be the workboard of the shop
        module by default.

        If no module, create one.
        """
        try:
            module_class = self.kwargs['module_class']
        except KeyError:
            module_class = self.module_class
            
        if module_class == SelfSaleModule:
            self.module, created = SelfSaleModule.objects.get_or_create(
                shop=self.shop)
            self.success_url = reverse('url_module_selfsale_config')
        elif module_class == OperatorSaleModule:
            self.module, created = OperatorSaleModule.objects.get_or_create(
                shop=self.shop)
            self.success_url = reverse(
                'url_module_operatorsale_config')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShopModuleMixin, self).get_context_data(**kwargs)
        context['module'] = self.module
        return context


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

    def add_shop_object(self):
        try:
            self.shop = Shop.objects.get(pk=self.kwargs['shop_pk'])
        except ObjectDoesNotExist:
            raise Http404

    def has_permission(self):
        has_perms = super().has_permission()
        if not has_perms:
            return False
        else:
            self.add_shop_object()
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        return context
