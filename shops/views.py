from django.shortcuts import render, redirect
from django.views.generic import FormView, View
from django.db.models import Q

from shops.models import *
from shops.forms import *
from finances.models import *
from borgia.utils import *
from settings_data.utils import settings_safe_get


class ProductList(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                  GroupLateralMenuFormMixin):
    template_name = 'shops/product_list.html'
    perm_codename = 'list_product'
    lm_active = 'lm_product_list'
    form_class = ProductListForm

    search = None
    shop_query = None

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['product_list'] = self.form_query(
            Product.objects.filter(is_removed=False))
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ProductList, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form

    def form_valid(self, form):
        try:
            if form.cleaned_data['shop']:
                self.shop_query = form.cleaned_data['shop']
        except KeyError:
            pass

        if form.cleaned_data['search']:
            self.search = form.cleaned_data['search']

        return self.get(self.request, self.args, self.kwargs)

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


class ProductCreate(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                    GroupLateralMenuFormMixin):
    template_name = 'shops/product_create.html'
    perm_codename = 'add_product'
    lm_active = 'lm_product_create'
    form_class = ProductCreateForm

    def form_valid(self, form):
        if self.shop:
            shop = self.shop
        else:
            shop=form.cleaned_data['shop']
        if form.cleaned_data['on_quantity']:
            Product.objects.create(
                name=form.cleaned_data['name'],
                shop=shop,
                unit=form.cleaned_data['unit'],
                correcting_factor=1
            )
        else:
            Product.objects.create(
                name=form.cleaned_data['name'],
                shop=shop,
                correcting_factor=1
            )
        return redirect(reverse('url_product_list',
                        kwargs={'group_name': self.group.name}))

    def get_initial(self):
        initial = super(ProductCreate, self).get_initial()
        initial['purchase_date'] = now
        initial['on_quantity'] = False
        return initial

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        context['shop'] = self.shop
        context['group'] = self.group
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ProductCreate, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form


class ProductDeactivate(GroupPermissionMixin, ProductShopFromGroupMixin, View,
                        GroupLateralMenuMixin):
    """
    Deactivate a product and redirect to the retrieve of the product.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the product
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'shops/product_deactivate.html'
    success_url = None
    perm_codename = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Set to True or False, activation is reversible.
        if self.object.is_active is True:
            self.object.is_active = False
        else:
            self.object.is_active = True
        self.object.save()

        return redirect(reverse('url_product_retrieve',
                        kwargs={'group_name': self.group.name,
                                'pk': self.object.pk}))


class ProductRemove(GroupPermissionMixin, ProductShopFromGroupMixin, View,
                        GroupLateralMenuMixin):
    """
    Remove a product and redirect to the list of products.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the product
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'shops/product_remove.html'
    success_url = None
    perm_codename = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        # Set always to True, removing is non-reversible.
        self.object.is_removed = True
        self.object.save()

        # Delete all category_product which use the product.
        CategoryProduct.objects.filter(product=self.object).delete()

        return redirect(reverse('url_product_list',
                        kwargs={'group_name': self.group.name}))


class ProductRetrieve(GroupPermissionMixin, ProductShopFromGroupMixin, View,
                      GroupLateralMenuMixin):
    """
    Retrieve a Product.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the product
    :param self.perm_codename: codename of the permission checked.
    """
    template_name = 'shops/product_retrieve.html'
    perm_codename = None

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['object'] = self.object
        return render(request, self.template_name, context=context)


class ProductUpdate(GroupPermissionMixin, ProductShopFromGroupMixin, FormView,
                    GroupLateralMenuFormMixin):
    """
    Update a product and redirect to the workboard of the group.

    :param kwargs['group_name']: name of the group used.
    :param kwargs['pk']: pk of the product
    :param self.perm_codename: codename of the permission checked.
    """
    form_class = ProductUpdateForm
    template_name = 'shops/product_update.html'
    success_url = None
    perm_codename = None

    def get_context_data(self, **kwargs):
        context = super(ProductUpdate, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def get_initial(self):
        initial = super(ProductUpdate, self).get_initial()
        for k in ProductUpdateForm().fields.keys():
            initial[k] = getattr(self.object, k)
        return initial

    def form_valid(self, form):
        for k in form.fields.keys():
            if form.cleaned_data[k] != getattr(self.object, k):
                setattr(self.object, k, form.cleaned_data[k])
        self.object.save()
        return super(ProductUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse('url_product_retrieve',
                       kwargs={'group_name': self.group.name,
                               'pk': self.object.pk})


class ProductUpdatePrice(GroupPermissionMixin, ProductShopFromGroupMixin,
                         FormView, GroupLateralMenuFormMixin):
    """
    """
    form_class = ProductUpdatePriceForm
    template_name = 'shops/product_update_price.html'
    success_url = None
    perm_codename = 'change_price_product'

    def get_context_data(self, **kwargs):
        context = super(ProductUpdatePrice, self).get_context_data(**kwargs)
        context['object'] = self.object
        context['margin_profit'] = settings_safe_get('MARGIN_PROFIT').get_value()
        return context

    def get_initial(self):
        initial = super(ProductUpdatePrice, self).get_initial()
        initial['is_manual'] = self.object.is_manual
        initial['manual_price'] = self.object.manual_price
        return initial

    def get_success_url(self):
        return reverse('url_product_update_price',
                       kwargs={'group_name': self.group.name,
                               'pk': self.object.pk})

    def form_valid(self, form):
        self.object.is_manual = form.cleaned_data['is_manual']
        self.object.manual_price = form.cleaned_data['manual_price']
        self.object.save()
        return super(ProductUpdatePrice, self).form_valid(form)


class ShopCreate(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    template_name = 'shops/shop_create.html'
    perm_codename = 'add_shop'
    lm_active = 'lm_shop_create'
    form_class = ShopCreateForm
    perm_chiefs = ['add_user', 'retrieve_user', 'list_user', 'supply_money_user', 'add_product',
                   'change_product', 'retrieve_product', 'list_product',
                   'list_sale', 'retrieve_sale', 'use_operatorsalemodule',
                   'add_stockentry', 'retrieve_stockentry', 'list_stockentry',
                   'add_inventory', 'retrieve_inventory', 'list_inventory', 'change_price_product']
    perm_associates = ['add_user', 'retrieve_user', 'list_user', 'supply_money_user', 'add_product',
                       'change_product', 'retrieve_product', 'list_product',
                       'list_sale', 'retrieve_sale', 'use_operatorsalemodule',
                       'add_stockentry', 'retrieve_stockentry', 'list_stockentry',
                       'add_inventory', 'retrieve_inventory', 'list_inventory']

    def form_valid(self, form):
        """
        Create the shop instance and relating groups and permissions.
        """
        shop = Shop.objects.create(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            color=form.cleaned_data['color'])

        content_type = ContentType.objects.get(app_label='users', model='user')
        manage_chiefs = Permission.objects.create(
            name='Gérer le groupe des chiefs du magasin '+shop.name,
            codename='manage_group_chiefs-'+shop.name,
            content_type=content_type
        )
        manage_associates = Permission.objects.create(
            name='Gérer le groupe des associés du magasin '+shop.name,
            codename='manage_group_associates-'+shop.name,
            content_type=content_type
        )

        chiefs = Group.objects.create(
            name='chiefs-' + shop.name
        )
        associates = Group.objects.create(
            name='associates-' + shop.name
        )

        for codename in self.perm_chiefs:
            try:
                chiefs.permissions.add(
                    Permission.objects.get(codename=codename)
                )
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                pass
        chiefs.permissions.add(manage_associates)
        chiefs.save()
        for codename in self.perm_associates:
            try:
                associates.permissions.add(
                    Permission.objects.get(codename=codename)
                )
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                pass
        associates.save()

        presidents = Group.objects.get(pk=2)
        presidents.permissions.add(manage_chiefs)
        presidents.save()
        vice_presidents = Group.objects.get(pk=3)
        vice_presidents.permissions.add(manage_chiefs)
        vice_presidents.save()
        return super(ShopCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('url_shop_list',
                       kwargs={'group_name': self.group.name})


class ShopList(GroupPermissionMixin, View, GroupLateralMenuMixin):
    template_name = 'shops/shop_list.html'
    perm_codename = 'list_shop'
    lm_active = 'lm_shop_list'

    def get(self, request, *args, **kwargs):
        context = super(ShopList, self).get_context_data(**kwargs)
        context['shop_list'] = Shop.objects.all().exclude(pk=1).order_by(
            'name')
        return render(request, self.template_name, context=context)


class ShopUpdate(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    template_name = 'shops/shop_update.html'
    perm_codename = 'change_shop'
    form_class = ShopUpdateForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop_mod = Shop.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        return super(ShopUpdate, self).dispatch(request, *args, **kwargs)

    def get_initial(self, **kwargs):
        initial = super(ShopUpdate, self).get_initial(**kwargs)
        initial['description'] = self.shop_mod.description
        initial['color'] = self.shop_mod.color
        return initial

    def form_valid(self, form):
        self.shop_mod.description = form.cleaned_data['description']
        self.shop_mod.color = form.cleaned_data['color']
        self.shop_mod.save()

        self.success_url = reverse(
            'url_shop_list',
            kwargs={'group_name': self.group.name}
        )
        return super(ShopUpdate, self).form_valid(form)


# TODO: infos
class ShopCheckup(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                    GroupLateralMenuFormMixin):
    """
    You can see checkup of your group from shop only.
    If you're not from a group from shop, you need the permission 'list_shop'
    """
    template_name = 'shops/shop_checkup.html'
    perm_codename = None
    lm_active = 'lm_shop_list'
    form_class = ShopCheckupSearchForm

    date_begin = None
    date_end = None
    products = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.shop_mod = Shop.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist:
            raise Http404
        return super(ShopCheckup, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.shop:
            if self.shop != self.shop_mod:
                raise PermissionDenied
            self.lm_active = 'lm_shop_checkup'
        else:
            try:
                p = Permission.objects.get(codename='list_shop')
                if p not in self.group.permissions.all():
                    raise PermissionDenied
            except ObjectDoesNotExist:
                raise Http404
        return super(ShopCheckup, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.shop:
            if self.shop != self.shop_mod:
                raise Http404
            self.lm_active = 'lm_shop_checkup'
        else:
            try:
                p = Permission.objects.get(codename='list_shop')
                if p not in self.group.permissions.all():
                    raise PermissionDenied
            except ObjectDoesNotExist:
                raise Http404
        return super(ShopCheckup, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShopCheckup, self).get_context_data(**kwargs)
        context['stock'] = self.info_stock()
        context['transaction'] = self.info_transaction()
        context['info'] = self.info_checkup()
        context['shop_mod'] = self.shop_mod
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ShopCheckup, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop_mod
        return kwargs_form

    def form_valid(self, form):
        self.date_begin = form.cleaned_data['date_begin']
        self.date_end = form.cleaned_data['date_end']
        self.products = form.cleaned_data['products']
        return self.get(self.request, self.args, self.kwargs)

    def info_stock(self):
        return {}

    def info_transaction(self):
        # All
        q_sales = Sale.objects.filter(shop=self.shop_mod)
        value = sum(s.amount() for s in q_sales)
        nb = q_sales.count()
        try:
            mean = round(value / nb, 2)
        except (ZeroDivisionError, DivisionUndefined, DivisionByZero):
            mean = 0
        return {
            'value': value,
            'nb': nb,
            'mean': mean
        }

    def info_checkup(self):
        q_sale = Sale.objects.filter(shop=self.shop_mod)
        if self.products:
            q_sale = q_sale.filter(products__pk__in=[p.pk for p in self.products])
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
