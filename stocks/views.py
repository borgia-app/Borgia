from django.shortcuts import render, redirect, Http404, reverse
from functools import partial, wraps
from decimal import Decimal

from django.views.generic import FormView, View
from django.forms.formsets import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

from borgia.utils import (GroupPermissionMixin, GroupLateralMenuFormMixin,
                          ShopFromGroupMixin, ShopModuleMixin,
                          GroupLateralMenuMixin, shop_from_group,
                          lateral_menu)
from stocks.forms import StockEntryProductForm
from shops.models import Product


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
        stockentry = StockEntry.objects.create(operator=request.user)

        stockentry_form = self.form_class(request.POST)
        for form in stockentry_form.cleaned_data:
            """
            Even if html and js verify and ensure entries, you verify again here.
            """
            try:
                product = Product.objects.get(pk=form['product'].split('/')[0])
                if product.unit:
                    # Container
                    if product.unit == 'G':
                        if form['unit_quantity'] == 'G':
                            quantity = Decimal(form['quantity'])
                            if form['unit_amount'] == 'PACKAGE':
                                price = Decimal(form['amount'])
                            elif form['unit_amount'] == 'KG':
                                price = Decimal(form['amount'] * Decimal(form['quantity'] / 1000))
                        elif form['unit_quantity'] == 'KG':
                            quantity = Decimal(form['quantity'] * 1000)
                            if form['unit_amount'] == 'PACKAGE':
                                price = Decimal(form['amount'])
                            elif form['unit_amount'] == 'KG':
                                price = Decimal(form['amount'] * form['quantity'])
                    elif product.unit == 'CL':
                        if form['unit_quantity'] == 'CL':
                            quantity = Decimal(form['quantity'])
                            if form['unit_amount'] == 'PACKAGE':
                                price = Decimal(form['amount'])
                            elif form['unit_amount'] == 'L':
                                price = Decimal(form['amount'] * Decimal(form['quantity'] / 100))
                        elif form['unit_quantity'] == 'L':
                            quantity = Decimal(form['quantity'] * 100)
                            if form['unit_amount'] == 'PACKAGE':
                                price = Decimal(form['amount'])
                            elif form['unit_amount'] == 'L':
                                price = Decimal(form['amount'] * form['quantity'])
                else:
                    # Single product
                    quantity = form['quantity']
                    if form['unit_amount'] == 'UNIT':
                        price = Decimal(form['amount'] * form['quantity'])
                    elif form['unit_amount'] == 'PACKAGE':
                        price = Decimal(form['amount'])

                StockEntryProduct.objects.create(
                    stockentry=stockentry,
                    product=product,
                    quantity=quantity,
                    price=amount
                )

            except ObjectDoesNotExist:
                pass
            except ZeroDivisionError:
                pass

            return self.get(request, *args, **kwargs)
