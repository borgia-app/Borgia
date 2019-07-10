import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import formset_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from borgia.views import BorgiaFormView, BorgiaView
from shops.mixins import ShopMixin
from shops.models import Product
from stocks.forms import (AdditionnalDataInventoryForm,
                          AdditionnalDataStockEntryForm,
                          BaseInventoryProductFormSet, InventoryListDateForm,
                          InventoryProductForm, StockEntryListDateForm,
                          StockEntryProductForm)
from stocks.models import (Inventory, InventoryProduct, StockEntry,
                           StockEntryProduct)


class StockEntryListView(ShopMixin, BorgiaFormView):
    permission_required = 'stocks.view_stockentry'
    menu_type = 'shops'
    template_name = 'stocks/stockentry_list.html'
    form_class = StockEntryListDateForm
    lm_active = 'lm_stockentry_list'

    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stockentry_list'] = self.form_query(
            self.shop.stockentry_set.all())
        return context

    def get_form_kwargs(self):
        kwargs_form = super().get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form

    def form_valid(self, form):
        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']
        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']

        return self.get(self.request, self.args, self.kwargs)

    def form_query(self, query):
        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)

        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)
        return query


class StockEntryCreateView(ShopMixin, BorgiaView):
    """
    """
    permission_required = 'stocks.add_stockentry'
    menu_type = 'shops'
    template_name = 'stocks/stockentry_create.html'
    lm_active = 'lm_stockentry_create'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        stockentry_product_form = formset_factory(StockEntryProductForm,
                                                  extra=1)
        context['stockentry_form'] = stockentry_product_form(
            form_kwargs={'shop': self.shop})
        context['add_inventory_form'] = AdditionnalDataStockEntryForm()
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        stockentry = StockEntry.objects.create(
            operator=request.user, shop=self.shop)

        # TODO: Verify formset with django 2.x
        stockentry_product_form = formset_factory(StockEntryProductForm,
                                                  extra=1)
        stockentry_form = stockentry_product_form(
            request.POST, form_kwargs={'shop': self.shop, 'empty_permitted': False})
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
            reverse('url_stockentry_list',
                    kwargs={'shop_pk': self.shop.pk})
        )


class StockEntryRetrieveView(ShopMixin, BorgiaView):
    permission_required = 'stocks.view_stockentry'
    menu_type = 'shops'
    template_name = 'stocks/stockentry_retrieve.html'
    lm_active = 'lm_stockentry_list'

    def __init__(self):
        super().__init__()
        self.stockentry = None

    def add_stockentry_object(self):
        """
        Define stockentry object.
        Raise Http404 is stockentry doesn't exist.
        """
        try:
            self.stockentry = StockEntry.objects.get(pk=self.kwargs['stockentry_pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.stockentry.shop.pk != self.shop.pk:
            raise Http404

    def add_context_objects(self):
        """
        Override to add more context objects for the view.
        """
        super().add_context_objects()
        self.add_stockentry_object()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['stockentry'] = self.stockentry
        return render(request, self.template_name, context=context)


class InventoryListView(ShopMixin, BorgiaFormView):
    permission_required = 'stocks.view_inventory'
    menu_type = 'shops'
    template_name = 'stocks/inventory_list.html'
    form_class = InventoryListDateForm
    lm_active = 'lm_inventory_list'

    date_begin = None
    date_end = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory_list'] = self.form_query(
            self.shop.inventory_set.all())
        return context

    def get_form_kwargs(self):
        kwargs_form = super().get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form

    def form_valid(self, form):
        if form.cleaned_data['date_begin']:
            self.date_begin = form.cleaned_data['date_begin']
        if form.cleaned_data['date_end']:
            self.date_end = form.cleaned_data['date_end']

        return self.get(self.request, self.args, self.kwargs)

    def form_query(self, query):
        if self.date_begin:
            query = query.filter(
                datetime__gte=self.date_begin)
        if self.date_end:
            query = query.filter(
                datetime__lte=self.date_end)

        return query


class InventoryCreateView(ShopMixin, BorgiaView):
    """
    """
    permission_required = 'stocks.add_inventory'
    menu_type = 'shops'
    template_name = 'stocks/inventory_create.html'
    lm_active = 'lm_inventory_create'

    def get(self, request, *args, **kwargs):
        inventory_product_formset = formset_factory(InventoryProductForm,
                                                    formset=BaseInventoryProductFormSet,
                                                    extra=1)
        context = self.get_context_data(**kwargs)
        context['inventory_formset'] = inventory_product_formset(
            form_kwargs={'shop': self.shop})
        context['additionnal_data_form'] = AdditionnalDataInventoryForm()
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """
        Products in the shop (and active) but not listed in the form are
        included in the inventory with a quantity 0.
        """
        # TODO: Verify formset with django 2.x
        inventory_product_formset = formset_factory(InventoryProductForm,
                                                    formset=BaseInventoryProductFormSet,
                                                    extra=1)
        inventory_formset = inventory_product_formset(
            request.POST, form_kwargs={'shop': self.shop, 'empty_permitted': False})
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
                        kwargs={'shop_pk': self.shop.pk})
            )
        else:
            return self.get(request)


class InventoryRetrieveView(ShopMixin, BorgiaView):
    permission_required = 'stocks.view_inventory'
    menu_type = 'shops'
    template_name = 'stocks/inventory_retrieve.html'
    lm_active = 'lm_inventory_list'

    def __init__(self):
        super().__init__()
        self.inventory = None

    def add_inventory_object(self):
        """
        Define inventory object.
        Raise Http404 is inventory doesn't exist.
        """
        try:
            self.inventory = Inventory.objects.get(pk=self.kwargs['inventory_pk'])
        except ObjectDoesNotExist:
            raise Http404
        if self.inventory.shop.pk != self.shop.pk:
            raise Http404

    def add_context_objects(self):
        """
        Override to add more context objects for the view.
        """
        super().add_context_objects()
        self.add_inventory_object()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['inventory'] = self.inventory
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
