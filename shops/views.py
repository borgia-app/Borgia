from functools import partial, wraps

from django.shortcuts import render, redirect
from django.shortcuts import Http404
from django.views.generic import FormView, View
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.forms.formsets import formset_factory
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from shops.models import *
from shops.forms import *
from finances.models import *
from borgia.utils import *


class ProductList(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                  GroupLateralMenuFormMixin):
    template_name = 'shops/product_list.html'
    perm_codename = 'list_product'
    lm_active = 'lm_product_list'
    form_class = ProductListForm

    search = None
    type = None
    shop_query = None

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['product_list'] = self.form_query(
            ProductBase.objects.all().exclude(pk=1))
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

        if form.cleaned_data['type']:
            self.type = form.cleaned_data['type']

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
                | Q(description__icontains=self.search)
            )
        if self.type:
            query = query.filter(type=self.type)
        return query


class ProductCreate(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                    GroupLateralMenuFormMixin):
    template_name = 'shops/product_create.html'
    perm_codename = 'add_product'
    lm_active = 'lm_product_create'
    product_class = None

    def dispatch(self, request, *args, **kwargs):
        try:
            if kwargs['product_class'] is ProductBase:
                self.product_class = ProductBase
            if kwargs['product_class'] is ProductUnit:
                self.product_class = ProductUnit
        except KeyError:
            pass
        return super(ProductCreate, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.product_class is ProductBase:
            return ProductBaseCreateForm
        elif self.product_class is ProductUnit:
            return ProductUnitCreateForm
        else:
            return ProductCreateForm

    def form_valid(self, form):
        if self.product_class is None:
            self.form_valid_instance(form)
        if self.product_class is ProductBase:
            self.form_valid_productbase(form)
            self.success_url = reverse(
                'url_product_create', kwargs={'group_name': self.group.name}
            )
        if self.product_class is ProductUnit:
            self.form_valid_productunit(form)
            self.success_url = reverse(
                'url_productbase_create', kwargs={'group_name': self.group.name}
            )
        return redirect(reverse('url_product_list',
                        kwargs={'group_name': self.group.name}))

    def form_valid_instance(self, form):
        if form.cleaned_data['product_base'].type == 'container':
            if form.cleaned_data['product_base'].product_unit.type in ['meat', 'cheese']:
                product = Container.objects.create(price=(form.cleaned_data['price'] *1000/ form.cleaned_data['quantity']),
                                                   quantity_remaining=form.cleaned_data['quantity'],
                                                   purchase_date=form.cleaned_data['purchase_date'],
                                                   expiry_date=form.cleaned_data['expiry_date'],
                                                   place=form.cleaned_data['place'],
                                                   product_base=form.cleaned_data['product_base'])
            else:
                for i in range(0, form.cleaned_data['quantity']):
                    product = Container.objects.create(price=form.cleaned_data['price'],
                                                       purchase_date=form.cleaned_data['purchase_date'],
                                                       expiry_date=form.cleaned_data['expiry_date'],
                                                       place=form.cleaned_data['place'],
                                                       product_base=form.cleaned_data['product_base'],
                                                       quantity_remaining=form.cleaned_data['product_base'].quantity)
        elif form.cleaned_data['product_base'].type == 'single_product':
            for i in range(0, form.cleaned_data['quantity']):
                product = SingleProduct.objects.create(price=form.cleaned_data['price'],
                                                       purchase_date=form.cleaned_data['purchase_date'],
                                                       expiry_date=form.cleaned_data['expiry_date'],
                                                       place=form.cleaned_data['place'],
                                                       product_base=form.cleaned_data['product_base'])

    def form_valid_productbase(self, form):
        if self.shop:
            if form.cleaned_data['type'] == 'container':
                ProductBase.objects.create(
                    name=(
                        form.cleaned_data['product_unit'].get_type_display().capitalize()
                        + ' '
                        + form.cleaned_data['product_unit'].name
                        + ' '
                        + str(form.cleaned_data['quantity'])
                        + form.cleaned_data['product_unit'].get_unit_display()
                    ),
                    description=(
                        form.cleaned_data['product_unit'].get_type_display().capitalize()
                        + ' '
                        + form.cleaned_data['product_unit'].name
                        + ' '
                        + str(form.cleaned_data['quantity'])
                        + form.cleaned_data['product_unit'].get_unit_display()
                    ),
                    brand=form.cleaned_data['brand'],
                    type=form.cleaned_data['type'],
                    shop=self.shop,
                    quantity=form.cleaned_data['quantity'],
                    product_unit=form.cleaned_data['product_unit']
                )
            if form.cleaned_data['type'] == 'single_product':
                ProductBase.objects.create(
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['name'],
                    brand=form.cleaned_data['brand'],
                    type=form.cleaned_data['type'],
                    shop=self.shop
                )
        else:
            if form.cleaned_data['type'] == 'container':
                ProductBase.objects.create(
                    name=(
                        form.cleaned_data['product_unit'].get_type_display().capitalize()
                        + ' '
                        + form.cleaned_data['product_unit'].name
                        + ' '
                        + str(form.cleaned_data['quantity'])
                        + form.cleaned_data['product_unit'].get_unit_display()
                    ),
                    description=(
                        form.cleaned_data['product_unit'].get_type_display().capitalize()
                        + ' '
                        + form.cleaned_data['product_unit'].name
                        + ' '
                        + str(form.cleaned_data['quantity'])
                        + form.cleaned_data['product_unit'].get_unit_display()
                    ),
                    brand=form.cleaned_data['brand'],
                    type=form.cleaned_data['type'],
                    shop=form.cleaned_data['shop'],
                    quantity=form.cleaned_data['quantity'],
                    product_unit=form.cleaned_data['product_unit']
                )
            if form.cleaned_data['type'] == 'single_product':
                ProductBase.objects.create(
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['name'],
                    brand=form.cleaned_data['brand'],
                    type=form.cleaned_data['type'],
                    shop=form.cleaned_data['shop']
                )

    def form_valid_productunit(self, form):
        if self.shop:
            ProductUnit.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['name'],
                unit=form.cleaned_data['unit'],
                type=form.cleaned_data['type'],
                shop=self.shop
            )
        else:
            ProductUnit.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['name'],
                unit=form.cleaned_data['unit'],
                type=form.cleaned_data['type'],
                shop=form.cleaned_data['shop']
            )

    def get_initial(self):
        initial = super(ProductCreate, self).get_initial()
        if self.product_class is None:
            initial['purchase_date'] = now
        return initial

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        context['shop'] = self.shop
        context['group'] = self.group
        try:
            context['product_class'] = self.product_class._meta.model_name
        except AttributeError:
            pass
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ProductCreate, self).get_form_kwargs()
        kwargs_form['shop'] = self.shop
        return kwargs_form


class ProductDeactivate(GroupPermissionMixin, ProductShopFromGroupMixin, View,
                        GroupLateralMenuMixin):
    """
    Deactivate a product and redirect to the workboard of the group.

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
        if self.object.is_active is True:
            self.object.is_active = False
        else:
            self.object.is_active = True
        self.object.save()

        return redirect(reverse('url_product_retrieve',
                        kwargs={'group_name': self.group.name,
                                'pk': self.object.pk}))


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
        try:
            context['margin_profit'] = Setting.objects.get(
                name='MARGIN_PROFIT').get_value()
        except ObjectDoesNotExist:
            pass
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


class ProductStockRegularisation(GroupPermissionMixin, ProductShopFromGroupMixin,
                                 FormView, GroupLateralMenuFormMixin):
    """
    """
    form_class = ProductStockRegularisationForm
    template_name = 'shops/product_update_stock.html'
    success_url = None
    perm_codename = 'change_stock_product'

    def get_context_data(self, **kwargs):
        context = super(ProductStockRegularisation, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def get_form_kwargs(self):
        kwargs_form = super(ProductStockRegularisation, self).get_form_kwargs()
        kwargs_form['product_base'] = self.object
        return kwargs_form

    def get_initial(self):
        initial = super(ProductStockRegularisation, self).get_initial()
        initial['number'] = 1
        initial['type'] = 'out'
        return initial

    def get_success_url(self):
        return reverse('url_product_retrieve',
                       kwargs={'group_name': self.group.name,
                               'pk': self.object.pk})

    def form_valid(self, form):
        # 'in' -> add products to stock, specify it's a regulation
        # Inventory
        if form.cleaned_data['type'] == 'in':
            if self.object.get_moded_price() != 0:
                price = self.object.get_moded_price()
            else:
                try:
                    if self.object.type == 'container':
                        price = Container.objects.filter(
                            product_base=self.object
                        )[0].price
                    else:
                        price = SingleProduct.objects.filter(
                            product_base=self.object
                        )[0].price
                except KeyError:
                    pass  # managed in the form !
            justification_regularisation = 'add inventory'

            for i in range(0, form.cleaned_data['number']):
                if self.object.type == 'container':
                    Container.objects.create(
                        price=price,
                        purchase_date=now(),
                        place='stock',
                        quantity_remaining=self.object.quantity,
                        product_base=self.object,
                        stock_regularisation=True,
                        justification_regularisation=justification_regularisation
                    )
                else:
                    SingleProduct.objects.create(
                        price=price,
                        purchase_date=now(),
                        place='stock',
                        product_base=self.object,
                        stock_regularisation=True,
                        justification_regularisation=justification_regularisation
                    )

        # 'out' -> remove products to stock, specify it's a regulation
        else:
            # Sell to someone
            if form.cleaned_data['occasion'] == 'sell':
                sell_price = form.cleaned_data['sell_price']
                justification_regularisation = form.cleaned_data['justification']
            # Inventory
            else:
                sell_price = self.object.get_moded_price()
                justification_regularisation = 'remove inventory'

            if self.object.type == 'container':
                list = Container.objects.filter(
                    product_base=self.object,
                    is_sold=False
                ).reverse()
            else:
                list = SingleProduct.objects.filter(
                    product_base=self.object,
                    is_sold=False
                ).reverse()
            for i in range(0, form.cleaned_data['number']):
                try:
                    c = list[i]
                    c.sell_price=sell_price
                    c.stock_regularisation=True
                    c.justification_regularisation=justification_regularisation
                    c.is_sold=True
                    c.save()
                except IndexError:
                    pass

        return super(ProductStockRegularisation, self).form_valid(form)


class ShopCreate(GroupPermissionMixin, FormView, GroupLateralMenuFormMixin):
    template_name = 'shops/shop_create.html'
    perm_codename = 'add_shop'
    lm_active = 'lm_shop_create'
    form_class = ShopCreateForm
    perm_chiefs = ['add_user', 'supply_money_user', 'add_product',
                   'change_product', 'retrieve_product', 'list_product',
                   'list_sale', 'retrieve_sale', 'use_operatorsalemodule']
    perm_associates = ['add_user', 'supply_money_user', 'add_product',
                       'change_product', 'retrieve_product', 'list_product',
                       'list_sale', 'retrieve_sale', 'use_operatorsalemodule']

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
            raise PermissionDenied
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
        q_container = Container.objects.filter(product_base__shop=self.shop_mod, is_sold=False)
        value_container = sum(c.price for c in q_container)
        nb_container = q_container.count()
        q_single_product = SingleProduct.objects.filter(product_base__shop=self.shop_mod, is_sold=False)
        value_single_product = sum(sp.price for sp in q_single_product)
        nb_single_product = q_single_product.count()
        return {
            'value': value_container + value_single_product,
            'nb': nb_container + nb_single_product
        }

    def info_transaction(self):
        # All
        q_sales = Sale.objects.filter(
            category='sale',
            wording='Vente '+self.shop_mod.name
        )
        value = sum(s.amount for s in q_sales)
        nb = q_sales.count()
        try:
            mean = round(value / nb, 2)
        except ZeroDivisionError:
            mean = 0
        return {
            'value': value,
            'nb': nb,
            'mean': mean
        }

    def info_checkup(self):
        ## Buy
        # Containers
        q_buy_container = Container.objects.filter(product_base__shop=self.shop_mod)
        if self.products:
            q_buy_container = q_buy_container.filter(product_base__pk__in=[c.pk for c in self.products])
        if self.date_begin:
            q_buy_container = q_buy_container.filter(purchase_date__gte=self.date_begin)
        if self.date_end:
            q_buy_container = q_buy_container.filter(purchase_date__lte=self.date_end)


        # Single products
        q_buy_single_product = SingleProduct.objects.filter(product_base__shop=self.shop_mod)
        if self.products:
            q_buy_single_product = q_buy_single_product.filter(product_base__pk__in=[c.pk for c in self.products])
        if self.date_begin:
            q_buy_single_product = q_buy_single_product.filter(purchase_date__gte=self.date_begin)
        if self.date_end:
            q_buy_single_product = q_buy_single_product.filter(purchase_date__lte=self.date_end)

        # Info
        buy_value_container = sum(c.price for c in q_buy_container)
        buy_nb_container = q_buy_container.count()
        buy_value_single_product = sum(sp.price for sp in q_buy_single_product)
        buy_nb_single_product = q_buy_single_product.count()


        ## Sale
        # From containers
        q_sale_container = SingleProductFromContainer.objects.filter(
            container__product_base__shop=self.shop_mod)
        if self.products:
            q_sale_container = q_sale_container.filter(
                container__product_base__pk__in=[c.pk for c in self.products])
        if self.date_begin:
            q_sale_container = q_sale_container.filter(
                sale__date__gte=self.date_begin)
        if self.date_end:
            q_sale_container = q_sale_container.filter(
                sale__date__lte=self.date_end)

        # Single products
        q_sale_single_product = SingleProduct.objects.filter(product_base__shop=self.shop_mod, is_sold=True)
        if self.products:
            q_sale_single_product = q_sale_single_product.filter(product_base__pk__in=[c.pk for c in self.products])
        if self.date_begin:
            q_sale_single_product = q_sale_single_product.filter(sale__date__gte=self.date_begin)
        if self.date_end:
            q_sale_single_product = q_sale_single_product.filter(sale__date__lte=self.date_end)


        # Info
        sale_value_from_container = sum(spfc.sale_price for spfc in q_sale_container)
        sale_nb_from_container = q_sale_container.count()
        sale_value_single_product = sum(sp.sale_price for sp in q_sale_single_product)
        sale_nb_single_product = q_sale_single_product.count()

        return {
            'buy': {
                'container': {
                    'value': buy_value_container,
                    'nb': buy_nb_container
                },
                'single_product': {
                    'value': buy_value_single_product,
                    'nb': buy_nb_single_product
                },
                'value': buy_value_container + buy_value_single_product,
                'nb': buy_nb_container + buy_nb_single_product
            },
            'sale': {
                'container': {
                    'value': sale_value_from_container,
                    'nb': sale_nb_from_container
                },
                'single_product': {
                    'value': sale_value_single_product,
                    'nb': sale_nb_single_product
                },
                'value': sale_value_from_container + sale_value_single_product,
                'nb': sale_nb_from_container + sale_nb_single_product
            }
        }


class ShopContainerCases(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                         GroupLateralMenuFormMixin):
    template_name = 'shops/shop_containercases.html'
    perm_codename = None
    lm_active = 'lm_containercases'
    form_class = None

    def get_form_class(self):
        if ContainerCase.objects.filter(shop=self.shop).count() == 0:
            extra = 1
        else:
            extra = 0
        return formset_factory(
            wraps(ShopContainerCaseForm)(
                partial(ShopContainerCaseForm, shop=self.shop)), extra=extra)

    def get_initial(self):
        containercases_data = []
        for c in ContainerCase.objects.filter(shop=self.shop):
            try:
                containercases_data.append(
                    {'name': c.name,
                     'base_container': c.product.product_base,
                     'pk': c.pk,
                     'percentage': c.product.estimated_quantity_remaining()[1]}
                )
            except AttributeError:
                containercases_data.append(
                    {'name': c.name,
                     'base_container': None,
                     'pk': c.pk,
                     'percentage': None}
                )
        return containercases_data

    def form_valid(self, form):
        list_pk = []
        list_product_pk = []
        for containercase_form in form:
            try:
                list_pk.append(containercase_form.cleaned_data['pk'])
                if containercase_form.cleaned_data['base_container']:
                    list_product_pk.append(ContainerCase.objects.get(pk=containercase_form.cleaned_data['pk']).product.pk)
            except KeyError:
                pass
            except AttributeError:
                pass
            except ObjectDoesNotExist:
                pass
        for containercase in ContainerCase.objects.filter(shop=self.shop):
            if containercase.pk not in list_pk:
                containercase.delete()

        for containercase_form in form:
            new_base = containercase_form.cleaned_data[
                'base_container']
            if containercase_form.cleaned_data['pk'] is not None:
                containercase = ContainerCase.objects.get(
                    pk=containercase_form.cleaned_data['pk'])
                containercase.name = containercase_form.cleaned_data[
                    'name']

                old = containercase.product

                if old:
                    if new_base:
                        if new_base != old.product_base:
                            old.is_sold = containercase_form.cleaned_data[
                                'is_sold']
                            old.save()
                            containercase.product = Container.objects.filter(
                                product_base=new_base,
                                is_sold=False).exclude(pk__in=list_product_pk)[0]
                            containercase.save()
                        else:
                            pass
                    else:
                        old.is_sold = containercase_form.cleaned_data[
                            'is_sold']
                        old.save()
                        containercase.product = None
                        containercase.save()
                else:
                    if new_base:
                        containercase.product = Container.objects.filter(
                            product_base=new_base,
                            is_sold=False).exclude(pk__in=list_product_pk)[0]
                        containercase.save()
                    else:
                        pass

            else:
                containercase = ContainerCase.objects.create(
                    name=containercase_form.cleaned_data['name'],
                    shop=self.shop
                )
                if containercase_form.cleaned_data['base_container']:
                    try:
                        containercase.product = Container.objects.filter(
                            product_base=new_base,
                            is_sold=False).exclude(pk__in=list_product_pk)[0]
                    except KeyError:
                        containercase.product = None
                containercase.save()

        return super(ShopContainerCases, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'url_shop_containercases',
            kwargs={'group_name': self.group.name}
        )
