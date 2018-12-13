from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
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
    permission_required_self = None
    permission_required_operator = None

    def __init__(self):
        self.shop = None
        self.module_class = None
        self.module = None

    def add_shop_object(self):
        """
        Define shop object. 
        Raise Http404 is shop doesn't exist.
        """
        try:
            self.shop = Shop.objects.get(pk=self.kwargs['shop_pk'])
        except ObjectDoesNotExist:
            raise Http404

    def add_module_object(self):
        """
        Define module object.
        Raise Http404 is module doesn't exist.
        """
        self.module_class = self.kwargs['module_class']
        if self.module_class == "self_sales":
            self.module = SelfSaleModule.objects.get_or_create(
                shop=self.shop)[0]
        elif self.module_class == "operator_sales":
            self.module = OperatorSaleModule.objects.get_or_create(
                shop=self.shop)[0]
        else:
            raise Http404

    def add_context_objects(self):
        """
        Define context objects
        """
        self.add_shop_object()
        self.add_module_object()

    def verify_permission(self, permission_required):
        if permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required_... attribute. Define {0}.permission_required_..., or override '
                '{0}.get_permission_required().'.format(self.__class__.__name__)
            )
        if isinstance(permission_required, str):
            perms = (permission_required,)
        else:
            perms = permission_required
        return perms

    def get_permission_required(self):
        """
        Override the method to check perms related to module.
        """
        if self.module_class == 'self_sales':
            return self.verify_permission(self.permission_required_self)
        elif self.module_class == 'operator_sales':
            return self.verify_permission(self.permission_required_operator)
        else:
            return self.handle_unexpected_module_class()
        
    def has_permission(self):
        """
        Define context object, only then check for permissions
        (Shop and modules need to be defined before checking perms)
        """
        self.add_context_objects()
        return super().has_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = self.shop
        context['module_class'] = self.module_class
        context['module'] = self.module
        return context

    def handle_unexpected_module_class(self):
        """
        Raise error when module_class is not expected
        """
        raise ImproperlyConfigured(
            'Error in {0}. {1} value should be either self_sales or operator_sales'.format(
                self.__class__.__name__, self.module_class)
            )
