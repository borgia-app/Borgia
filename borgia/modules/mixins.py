from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.http import Http404

from modules.models import Category, OperatorSaleModule, SelfSaleModule
from shops.mixins import ShopMixin


class ShopModuleMixin(ShopMixin):
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
        super().__init__()
        self.module_class = None
        self.module = None

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
        super().add_context_objects()
        self.add_module_object()

    def verify_permission(self, permission_required):
        if permission_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the permission_required_self/operator attribute. Define {0}.permission_required_self/operator, or override '
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module_class'] = self.module_class
        context['module'] = self.module
        context['categories'] = self.module.categories.all().order_by('order')
        return context

    def handle_unexpected_module_class(self):
        """
        Raise error when module_class is not expected
        """
        raise ImproperlyConfigured(
            'Error in {0}. {1} value should be either self_sales or operator_sales'.format(
                self.__class__.__name__, self.module_class)
            )


class ShopModuleCategoryMixin(ShopModuleMixin):
    """
    """

    def add_category_object(self):
        """
        Define category object.
        Raise Http404 is category doesn't exist.
        """
        try:
            self.category = Category.objects.get(pk=self.kwargs['category_pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.category.module.shop.pk != self.shop.pk:
            raise Http404
        if self.category.module.get_module_class() != self.module_class:
            raise Http404

    def add_context_objects(self):
        """
        Define context objects
        """
        super().add_context_objects()
        self.add_category_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
