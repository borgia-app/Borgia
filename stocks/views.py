from django.shortcuts import render, redirect, Http404, reverse
from functools import partial, wraps

from django.views.generic import FormView, View
from django.forms.formsets import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

from borgia.utils import (GroupPermissionMixin, GroupLateralMenuFormMixin,
                          ShopFromGroupMixin, ShopModuleMixin,
                          GroupLateralMenuMixin, shop_from_group,
                          lateral_menu)
from stocks.forms import StockEntryProductForm


class ShopStockEntryCreate(GroupPermissionMixin, ShopFromGroupMixin,
                                View, GroupLateralMenuMixin):
    """
    """
    template_name = 'stocks/shop_stock_entry_create.html'
    form_class = None
    perm_codename = None
    lm_active = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
            self.shop = shop_from_group(self.group)
        except ObjectDoesNotExist:
            raise Http404
        except ValueError:
            raise Http404
        self.form_class = formset_factory(wraps(StockEntryProductForm)(partial(StockEntryProductForm, shop=self.shop)), extra=1)
        return super(ShopStockEntryCreate,
                     self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['stockentry_form'] = self.form_class()
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        print('post')
        pass
