import decimal

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.base import View
from django.views.generic.edit import FormView

from borgia.utils import (GroupLateralMenuFormMixin, GroupLateralMenuMixin,
                          GroupPermissionMixin, ShopFromGroupMixin,
                          shop_from_group)
from shops.models import Product
from stocks.forms import (AdditionnalDataInventoryForm,
                          AdditionnalDataStockEntryForm,
                          BaseInventoryProductFormSet, InventoryListDateForm,
                          InventoryProductForm, StockEntryListDateForm,
                          StockEntryProductForm)
from stocks.models import (Inventory, InventoryProduct, StockEntry,
                           StockEntryProduct)


class StockEntryListView(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                     GroupLateralMenuFormMixin):
    template_name = 'stocks/stockentry_list.html'
    perm_codename = 'list_stockentry'
    lm_active = 'lm_stockentry_list'
    form_class = StockEntryListDateForm

    shop_query = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(StockEntryListView, self).get_context_data(**kwargs)
        context['stockentry_list'] = self.form_query(
            StockEntry.objects.all().order_by('-datetime'))
        return context

    def get_form_kwargs(self):
        kwargs_form = super(StockEntryListView, self).get_form_kwargs()
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


class StockEntryCreateView(GroupPermissionMixin, ShopFromGroupMixin,
                           View, GroupLateralMenuMixin):
    """
    """
    template_name = 'stocks/stock_entry_create.html'
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

        self.stock_entry_product_form = formset_factory(StockEntryProductForm,
                                                        extra=1)
        return super(StockEntryCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['stockentry_form'] = self.stock_entry_product_form(
            form_kwargs={'shop': self.shop})
        context['add_inventory_form'] = AdditionnalDataStockEntryForm()
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        stockentry = StockEntry.objects.create(
            operator=request.user, shop=self.shop)

        stockentry_form = self.stock_entry_product_form(
            request.POST, form_kwargs={'shop': self.shop})
        add_inventory_form = AdditionnalDataStockEntryForm(request.POST)

        if stockentry_form.is_valid() and add_inventory_form.is_valid():
            is_adding_inventory = False
            if add_inventory_form.cleaned_data['isAddingInventory'] == 'with':
                inventory = Inventory.objects.create(
                    operator=request.user, shop=self.shop)
                is_adding_inventory = True

            for form in stockentry_form.cleaned_data:
                try:
                    product = get_product_from_form(form['product'])
                    quantity = get_normalized_quantity(
                        product, form['unit_quantity'], form['quantity'])
                    price = get_normalized_price(
                        form['unit_quantity'], form['quantity'], form['unit_amount'], form['amount'])

                    StockEntryProduct.objects.create(
                        stockentry=stockentry,
                        product=product,
                        quantity=quantity,
                        price=price
                    )

                    # AJOUT DE L'INVENTAIRE SI BESOIN
                    if is_adding_inventory:
                        if form['unit_inventory'] and form['inventory_quantity']:
                            inventory_quantity = get_normalized_quantity(
                                product, form['unit_inventory'], form['inventory_quantity'])

                            InventoryProduct.objects.create(
                                inventory=inventory,
                                product=product,
                                quantity=inventory_quantity+quantity
                            )

                except ObjectDoesNotExist:
                    pass
                except (ZeroDivisionError, decimal.DivisionUndefined, decimal.DivisionByZero):
                    pass

        return redirect(
            reverse('url_stock_entry_list',
                    kwargs={'group_name': self.group.name})
        )


class StockEntryRetrieveView(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'stocks/stockentry_retrieve.html'
    perm_codename = 'retrieve_stockentry'
    lm_active = 'lm_stockentry_list'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = StockEntry.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        return super(StockEntryRetrieveView, self).dispatch(request, *args,
                                                        **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['stockentry'] = self.object
        return render(request, self.template_name, context=context)


class InventoryListView(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                    GroupLateralMenuFormMixin):
    template_name = 'stocks/inventory_list.html'
    perm_codename = 'list_inventory'
    lm_active = 'lm_inventory_list'
    form_class = InventoryListDateForm

    shop_query = None
    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super(InventoryListView, self).get_context_data(**kwargs)
        context['inventory_list'] = self.form_query(
            Inventory.objects.all().order_by('-datetime'))
        return context

    def get_form_kwargs(self):
        kwargs_form = super(InventoryListView, self).get_form_kwargs()
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


class InventoryCreateView(GroupPermissionMixin, ShopFromGroupMixin,
                          View, GroupLateralMenuMixin):
    """
    """
    template_name = 'stocks/inventory_create.html'
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

        self.inventory_product_formset = formset_factory(InventoryProductForm,
                                                         formset=BaseInventoryProductFormSet,
                                                         extra=1)

        self.additionnal_data_inventory_form = AdditionnalDataInventoryForm()

        return super(InventoryCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['inventory_formset'] = self.inventory_product_formset(
            form_kwargs={'shop': self.shop})
        context['additionnal_data_form'] = self.additionnal_data_inventory_form
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """
        Products in the shop (and active) but not listed in the form are
        included in the inventory with a quantity 0.
        """
        inventory_formset = self.inventory_product_formset(
            request.POST, form_kwargs={'shop': self.shop})
        additionnal_data_form = AdditionnalDataInventoryForm(request.POST)

        if inventory_formset.is_valid() and additionnal_data_form.is_valid():

            inventory = Inventory.objects.create(
                operator=request.user, shop=self.shop)

            # Ids in the form
            if inventory_formset.is_valid():
                for form in inventory_formset.cleaned_data:
                    try:
                        product = get_product_from_form(form['product'])
                        quantity = get_normalized_quantity(
                            product, form['unit_quantity'], form['quantity'])

                        InventoryProduct.objects.create(
                            inventory=inventory,
                            product=product,
                            quantity=quantity
                        )

                    except ObjectDoesNotExist:
                        pass

                if additionnal_data_form.is_valid():
                    if additionnal_data_form.cleaned_data['type'] == 'full':
                        # Ids not in the form but active in the shop
                        try:
                            for product in Product.objects.filter(shop=self.shop, is_removed=False, is_active=True).exclude(
                                    pk__in=[form['product'].split('/')[0] for form in inventory_formset.cleaned_data]):
                                InventoryProduct.objects.create(
                                    inventory=inventory,
                                    product=product,
                                    quantity=decimal.Decimal(0)
                                )

                        except ObjectDoesNotExist:
                            pass
                        except (ZeroDivisionError, decimal.DivisionUndefined, decimal.DivisionByZero):
                            pass

                # Update all correcting factors listed
                inventory.update_correcting_factors()

            return redirect(
                reverse('url_inventory_list',
                        kwargs={'group_name': self.group.name})
            )
        else:
            return self.get(request)


class InventoryRetrieveView(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'stocks/inventory_retrieve.html'
    perm_codename = 'retrieve_inventory'
    lm_active = 'lm_inventory_list'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.object = Inventory.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404

        return super(InventoryRetrieveView, self).dispatch(request, *args,
                                                       **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['inventory'] = self.object
        return render(request, self.template_name, context=context)


def get_product_from_form(form_product):
    return Product.objects.get(pk=form_product.split('/')[0])


def get_normalized_quantity(product, form_unit_quantity, form_quantity):
    # Container
    if product.unit:
        if product.unit == 'G':
            if form_unit_quantity == 'G':
                quantity = decimal.Decimal(form_quantity)
            elif form_unit_quantity == 'KG':
                quantity = decimal.Decimal(form_quantity * 1000)
        elif product.unit == 'CL':
            if form_unit_quantity == 'CL':
                quantity = decimal.Decimal(form_quantity)
            elif form_unit_quantity == 'L':
                quantity = decimal.Decimal(form_quantity * 100)
    else:
        # Single product
        quantity = form_quantity

    return quantity


def get_normalized_price(form_unit_quantity, form_quantity, form_unit_amount, form_amount):
    # Container
    if form_unit_amount == 'PACKAGE':
        price = decimal.Decimal(form_amount)
    else:
        if form_unit_quantity == 'G' and form_unit_amount == 'KG':
            price = decimal.Decimal(
                form_amount * decimal.Decimal(form_quantity / 1000))
        elif form_unit_quantity == 'CL' and form_unit_amount == 'L':
            price = decimal.Decimal(
                form_amount * decimal.Decimal(form_quantity / 100))
        else:
            price = decimal.Decimal(form_amount * form_quantity)

    return price
