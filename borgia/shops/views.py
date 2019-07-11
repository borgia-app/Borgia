#-*- coding: utf-8 -*-

import datetime
import decimal

from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse

from borgia.views import BorgiaFormView, BorgiaView
from configurations.utils import configuration_get
from modules.models import CategoryProduct
from sales.models import Sale
from shops.forms import (ProductCreateForm, ProductListForm, ProductUpdateForm,
                         ProductUpdatePriceForm, ShopCheckupSearchForm,
                         ShopCreateForm, ShopUpdateForm)
from shops.mixins import ProductMixin, ShopMixin
from shops.models import Product, Shop



class ShopCreate(LoginRequiredMixin, PermissionRequiredMixin, BorgiaFormView):
    permission_required = 'shops.add_shop'
    menu_type = 'managers'
    template_name = 'shops/shop_create.html'
    lm_active = 'lm_shop_create'
    form_class = ShopCreateForm

    def __init__(self):
        self.shop = None

    def form_valid(self, form):
        """
        Create the shop instance and relating groups and permissions.
        """
        shop = Shop.objects.create(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            color=form.cleaned_data['color'])

        self.shop = shop
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_shop_checkup', kwargs={'shop_pk': self.shop.pk})


class ShopList(LoginRequiredMixin, PermissionRequiredMixin, BorgiaView):
    """
    View that list the shops.
    """
    permission_required = 'shops.view_shop'
    menu_type = 'managers'
    template_name = 'shops/shop_list.html'
    lm_active = 'lm_shop_list'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop_list'] = Shop.objects.all().order_by(
            'name')
        return render(request, self.template_name, context=context)


class ShopUpdate(ShopMixin, BorgiaFormView):
    permission_required = 'shops.change_shop'
    menu_type = 'shops'
    template_name = 'shops/shop_update.html'
    form_class = ShopUpdateForm

    def get_initial(self):
        initial = super().get_initial()
        initial['description'] = self.shop.description
        initial['color'] = self.shop.color
        return initial

    def form_valid(self, form):
        self.shop.description = form.cleaned_data['description']
        self.shop.color = form.cleaned_data['color']
        self.shop.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_shop_checkup', kwargs={'shop_pk': self.shop.pk})


class ShopCheckup(ShopMixin, BorgiaFormView):
    """
    Display data about a shop.

    You can see checkup of your own shop only.
    If you're not a manager of a shop, you need the permission 'view_shop'
    """
    permission_required = 'shops.view_shop'
    menu_type = 'shops'
    template_name = 'shops/shop_checkup.html'
    form_class = ShopCheckupSearchForm
    lm_active = 'lm_shop_checkup'

    date_begin = None
    date_end = None
    products = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock'] = self.info_stock()
        context['transaction'] = self.info_transaction()
        context['info'] = self.info_checkup()
        return context

    def get_form_kwargs(self):
        kwargs_form = super().get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form

    def form_valid(self, form):
        self.date_begin = form.cleaned_data['date_begin']
        self.date_end = form.cleaned_data['date_end']
        self.products = form.cleaned_data['products']
        return super().form_valid(form)

    def info_stock(self):
        return {}

    def info_transaction(self):
        # All
        q_sales = Sale.objects.filter(shop=self.shop)
        value = sum(s.amount() for s in q_sales)
        nb = q_sales.count()
        try:
            mean = round(value / nb, 2)
        except (ZeroDivisionError, decimal.DivisionByZero, decimal.DivisionUndefined):
            mean = 0
        return {
            'value': value,
            'nb': nb,
            'mean': mean
        }

    def info_checkup(self):
        q_sale = Sale.objects.filter(shop=self.shop)
        if self.products:
            q_sale = q_sale.filter(
                products__pk__in=[p.pk for p in self.products])
        if self.date_begin:
            q_sale = q_sale.filter(datetime__gte=self.date_begin)
        if self.date_end:
            q_sale = q_sale.filter(datetime__lte=self.date_end)
        sale_value = sum(s.amount() for s in q_sale)
        sale_nb = q_sale.count()
        return {
            'sale': {
                'value': sale_value,
                'nb': sale_nb
            }
        }


class ShopWorkboard(ShopMixin, BorgiaView):
    permission_required = 'shops.view_shop'
    menu_type = 'shops'
    template_name = 'shops/shop_workboard.html'
    lm_active = 'lm_workboard'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sale_list'] = self.get_sales()
        context['purchase_list'] = self.get_purchases()
        return render(request, self.template_name, context=context)

    def get_sales(self):
        sales = {}
        s_list = Sale.objects.filter(shop=self.shop).order_by('-datetime')
        sales['weeks'] = self.weeklist(
            datetime.datetime.now() - datetime.timedelta(days=30),
            datetime.datetime.now())
        sales['data_weeks'] = self.sale_data_weeks(s_list, sales['weeks'])[0]
        sales['total'] = self.sale_data_weeks(s_list, sales['weeks'])[1]
        sales['all'] = s_list[:7]
        return sales

    # TODO: purchases with stock
    @staticmethod
    def get_purchases():
        purchases = {}
        return purchases

    # TODO: purchases with stock
    @staticmethod
    def purchase_data_weeks(weeks):
        amounts = [0 for _ in range(0, len(weeks))]
        total = 0

        return amounts, total

    @staticmethod
    def sale_data_weeks(weeklist, weeks):
        amounts = [0 for _ in range(0, len(weeks))]
        total = 0
        for obj in weeklist:
            string = (str(obj.datetime.isocalendar()[1])
                      + '-' + str(obj.datetime.year))
            if string in weeks:
                amounts[weeks.index(string)] += obj.amount()
                total += obj.amount()
        return amounts, total

    @staticmethod
    def weeklist(start, end):
        weeklist = []
        for i in range(start.year, end.year+1):
            week_start = 1
            week_end = 52
            if i == start.year:
                week_start = start.isocalendar()[1]
            if i == end.year:
                week_end = end.isocalendar()[1]
            weeklist += [str(j) + '-' + str(i) for j in range(
                week_start, week_end+1)]
        return weeklist


class ProductList(ShopMixin, BorgiaFormView):
    permission_required = 'shops.view_product'
    menu_type = 'shops'
    template_name = 'shops/product_list.html'
    form_class = ProductListForm
    lm_active = 'lm_product_list'

    search = None
    shop_query = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_list'] = self.form_query(
            Product.objects.filter(is_removed=False))
        return context

    def form_valid(self, form):
        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']

        return super().form_valid(form)

    def form_query(self, query):
        if self.shop:
            query = query.filter(shop=self.shop)
        else:
            if self.shop_query:
                query = query.filter(shop=self.shop_query)
        if self.search:
            query = query.filter(
                Q(name__icontains=self.search)
            )
        return query


class ProductCreate(ShopMixin, BorgiaFormView):
    permission_required = 'shops.add_product'
    menu_type = 'shops'
    template_name = 'shops/product_create.html'
    form_class = ProductCreateForm
    lm_active = 'lm_product_create'

    def __init__(self):
        super().__init__()
        self.product = None

    def get_initial(self):
        initial = super().get_initial()
        initial['on_quantity'] = False
        return initial

    def form_valid(self, form):
        if form.cleaned_data['on_quantity']:
            product = Product.objects.create(
                name=form.cleaned_data['name'],
                shop=self.shop,
                unit=form.cleaned_data['unit'],
                correcting_factor=1
            )
        else:
            product = Product.objects.create(
                name=form.cleaned_data['name'],
                shop=self.shop,
                correcting_factor=1
            )
        self.product = product
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_product_retrieve', kwargs={
            'shop_pk': self.shop.pk,
            'product_pk': self.product.pk})


class ProductDeactivate(ProductMixin, BorgiaView):
    """
    Deactivate a product and redirect to the retrieve of the product.
    """
    permission_required = 'shops.delete_product'
    menu_type = 'shops'
    template_name = 'shops/product_deactivate.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Set to True or False, activation is reversible.
        if self.product.is_active is True:
            self.product.is_active = False
        else:
            self.product.is_active = True
        self.product.save()

        return redirect(reverse('url_product_retrieve',
                                kwargs={'shop_pk': self.shop.pk,
                                        'product_pk': self.product.pk}))


class ProductRemove(ProductMixin, BorgiaView):
    """
    Remove a product and redirect to the list of products.
    """
    permission_required = 'shops.change_product'
    menu_type = 'shops'
    template_name = 'shops/product_remove.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Set always to True, removing is non-reversible.
        self.product.is_removed = True
        self.product.save()

        # Delete all category_product which use the product.
        CategoryProduct.objects.filter(product=self.product).delete()

        return redirect(reverse('url_product_list', kwargs={'shop_pk': self.shop.pk}))


class ProductRetrieve(ProductMixin, BorgiaView):
    """
    Retrieve a Product.

    :param kwargs['shop_pk']: name of the group used.
    :param kwargs['product_pk']: pk of the product
    """
    permission_required = 'shops.view_product'
    menu_type = 'shops'
    template_name = 'shops/product_retrieve.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context=context)


class ProductUpdate(ProductMixin, BorgiaFormView):
    """
    Update a product and redirect to the product.

    :param kwargs['shop_pk']: pk of the shop
    :param kwargs['product_pk']: pk of the product
    """
    permission_required = 'shops.change_product'
    menu_type = 'shops'
    template_name = 'shops/product_update.html'
    form_class = ProductUpdateForm
    model = Product

    def get_initial(self):
        initial = super().get_initial()
        initial['name'] = self.product.name
        return initial

    def form_valid(self, form):
        self.product.name = form.cleaned_data['name']
        self.product.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_product_retrieve',
                       kwargs={'shop_pk': self.shop.pk,
                               'product_pk': self.product.pk})


class ProductUpdatePrice(ProductMixin, BorgiaFormView):
    """
    Update the price of a product and redirect to the product.

    :param kwargs['shop_pk']: pk of the shop
    :param kwargs['product_pk']: pk of the product
    """
    permission_required = 'shops.change_price_product'
    menu_type = 'shops'
    template_name = 'shops/product_update_price.html'
    form_class = ProductUpdatePriceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['margin_profit'] = configuration_get(
            'MARGIN_PROFIT').get_value()
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['is_manual'] = self.product.is_manual
        initial['manual_price'] = self.product.manual_price
        return initial

    def form_valid(self, form):
        self.product.is_manual = form.cleaned_data['is_manual']
        self.product.manual_price = form.cleaned_data['manual_price']
        self.product.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('url_product_retrieve',
                       kwargs={'shop_pk': self.shop.pk,
                               'product_pk': self.product.pk})
