from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from finances.models import Sale
from shops.mixins import ShopPermissionAndContextMixin, LateralMenuShopsMixin


class SalePermissionAndContextMixin(ShopPermissionAndContextMixin):
    """
    Mixin that check permission and give context for sales
    """
    def add_sale_object(self):
        """
        Define Sale object.
        Raise Http404 is sale doesn't exist.
        """
        try:
            self.sale = Sale.objects.get(pk=self.kwargs['sale_pk'])
        except ObjectDoesNotExist:
            raise Http404

        if self.sale.shop != self.shop:
            raise Http404

    def add_context_objects(self):
        """
        Override to add more context objects for the view.
        """
        super().add_context_objects()
        self.add_sale_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale'] = self.sale
        return context


class SaleMixin(SalePermissionAndContextMixin, LateralMenuShopsMixin):
    """
    Mixin that check permission, give context for sales and add SHOPS lateral menu.
    """