from django.shortcuts import render, redirect, Http404, reverse
from functools import partial, wraps
from decimal import Decimal, DivisionUndefined, DivisionByZero

from django.views.generic import FormView, View
from django.forms.formsets import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

from borgia.utils import (GroupPermissionMixin, GroupLateralMenuFormMixin,
                          ShopFromGroupMixin,
                          GroupLateralMenuMixin, shop_from_group)
from stocks.forms import (StockEntryProductForm, StockEntryListDateForm,
                            InventoryListDateForm, InventoryProductForm)
from stocks.models import StockEntry, StockEntryProduct, Inventory, InventoryProduct
from shops.models import Product


class ShopStockEntryCreate(GroupPermissionMixin, ShopFromGroupMixin,
                                View, GroupLateralMenuMixin):
    """
    """
    template_name = 'stocks/shop_stock_entry_create.html'
    form_class = None
    perm_codename = 'add_stockentry'
    lm_active = 'lm_stockentry_create'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
            self.shop = shop_from_group(self.group)
            if self.shop is None:
                raise Http404
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
        stockentry = StockEntry.objects.create(operator=request.user, shop=self.shop)

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
                    price=price
                )

            except ObjectDoesNotExist:
                pass
            except (ZeroDivisionError, DivisionUndefined, DivisionByZero):
                pass

        return redirect(
            reverse('url_stock_entry_list',
                           kwargs={'group_name': self.group.name})
                    )


class StockEntryList(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                  GroupLateralMenuFormMixin):
    template_name = 'stocks/stockentry_list.html'
    perm_codename = 'list_stockentry'
    lm_active = 'lm_stockentry_list'
    form_class = StockEntryListDateForm

    shop_query = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(StockEntryList, self).get_context_data(**kwargs)
        context['stockentry_list'] = self.form_query(
            StockEntry.objects.all().order_by('-datetime'))
        return context

    def get_form_kwargs(self):
        kwargs_form = super(StockEntryList, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form

    def form_valid(self, form):
        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']

        try:
            if form.cleaned_data['shop']:
                self.shop_query = form.cleaned_data['shop']
        except KeyError:
            pass

        return self.get(self.request, self.args, self.kwargs)

    def form_query(self, query):
        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

        if self.shop:
            query = query.filter(shop=self.shop)
        else:
            if self.shop_query:
                query = query.filter(shop=self.shop_query)

        return query


class StockEntryRetrieve(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'stocks/stockentry_retrieve.html'
    perm_codename = 'retrieve_stockentry'
    lm_active = 'lm_stockentry_list'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = StockEntry.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        return super(StockEntryRetrieve, self).dispatch(request, *args,
                                                       **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)


class ShopInventoryCreate(GroupPermissionMixin, ShopFromGroupMixin,
                                View, GroupLateralMenuMixin):
    """
    """
    template_name = 'stocks/shop_inventory_create.html'
    form_class = None
    perm_codename = 'add_inventory'
    lm_active = 'lm_inventory_create'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.group = Group.objects.get(name=kwargs['group_name'])
            self.shop = shop_from_group(self.group)
            if self.shop is None:
                raise Http404
        except ObjectDoesNotExist:
            raise Http404
        except ValueError:
            raise Http404
        self.form_class = formset_factory(wraps(InventoryProductForm)(partial(InventoryProductForm, shop=self.shop)), extra=1)
        return super(ShopInventoryCreate,
                     self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['inventory_form'] = self.form_class()
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """
        Products in the shop (and active) but not listed in the form are
        included in the inventory with a quantity 0.
        """
        inventory = Inventory.objects.create(operator=request.user, shop=self.shop)

        inventory_form = self.form_class(request.POST)

        # Ids in the form
        for form in inventory_form.cleaned_data:
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
                        elif form['unit_quantity'] == 'KG':
                            quantity = Decimal(form['quantity'] * 1000)
                    elif product.unit == 'CL':
                        if form['unit_quantity'] == 'CL':
                            quantity = Decimal(form['quantity'])
                        elif form['unit_quantity'] == 'L':
                            quantity = Decimal(form['quantity'] * 100)
                else:
                    # Single product
                    quantity = form['quantity']

                InventoryProduct.objects.create(
                    inventory=inventory,
                    product=product,
                    quantity=quantity
                )

            except ObjectDoesNotExist:
                pass
            except (ZeroDivisionError, DivisionUndefined, DivisionByZero):
                pass

        # Ids not in the form but active in the shop
        try:
            for product in Product.objects.filter(shop=self.shop, is_removed=False, is_active=True).exclude(
                        pk__in=[form['product'].split('/')[0] for form in inventory_form.cleaned_data]):
                InventoryProduct.objects.create(
                    inventory=inventory,
                    product=product,
                    quantity=Decimal(0)
                )

        except ObjectDoesNotExist:
            pass
        except (ZeroDivisionError, DivisionUndefined, DivisionByZero):
            pass

        # Update all correcting factors listed
        inventory.update_correcting_factors()

        return redirect(
            reverse('url_inventory_list',
                           kwargs={'group_name': self.group.name})
                    )


class InventoryList(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                  GroupLateralMenuFormMixin):
    template_name = 'stocks/inventory_list.html'
    perm_codename = 'list_inventory'
    lm_active = 'lm_inventory_list'
    form_class = InventoryListDateForm

    shop_query = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(InventoryList, self).get_context_data(**kwargs)
        context['inventory_list'] = self.form_query(
            Inventory.objects.all().order_by('-datetime'))
        return context

    def get_form_kwargs(self):
        kwargs_form = super(InventoryList, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form

    def form_valid(self, form):
        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']

        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']

        try:
            if form.cleaned_data['shop']:
                self.shop_query = form.cleaned_data['shop']
        except KeyError:
            pass

        return self.get(self.request, self.args, self.kwargs)

    def form_query(self, query):
        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

        if self.shop:
            query = query.filter(shop=self.shop)
        else:
            if self.shop_query:
                query = query.filter(shop=self.shop_query)

        return query


class InventoryRetrieve(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'stocks/inventory_retrieve.html'
    perm_codename = 'retrieve_inventory'
    lm_active = 'lm_inventory_list'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = Inventory.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        return super(InventoryRetrieve, self).dispatch(request, *args,
                                                       **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)
