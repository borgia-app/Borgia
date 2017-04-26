from django.core import serializers
from math import ceil
from functools import partial, wraps

from django.shortcuts import render, force_text, HttpResponseRedirect, redirect
from django.shortcuts import HttpResponse, Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.auth import logout
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.forms.formsets import formset_factory

from shops.models import *
from shops.forms import *
from users.models import User
from finances.models import *
from notifications.models import notify
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
        return super(ProductCreate, self).form_valid(form)

    def form_valid_instance(self, form):
        if form.cleaned_data['product_base'].type == 'container':
            if form.cleaned_data['product_base'].product_unit.type in ['meat', 'cheese']:
                product = Container.objects.create(price=(form.cleaned_data['price'] *1000/ form.cleaned_data['quantity'])*form.cleaned_data['product_base'].quantity,
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
                                                       quantity_remaining=ProductBase.objects.get(pk=form.cleaned_data['product_base']).quantity)
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
        for containercase_form in form:
            print(containercase_form)
            try:
                list_pk.append(containercase_form.cleaned_data['pk'])
            except KeyError:
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
                try:
                    old_base = containercase.product.product_base
                    if (old_base != new_base):
                        if old:
                            old.is_sold = containercase_form.cleaned_data[
                                'is_sold']
                            old.save()
                except AttributeError:
                    pass
                if new_base:
                    try:
                        containercase.product = Container.objects.filter(
                            product_base=new_base,
                            is_sold=False)[0]
                    except KeyError:
                        containercase.product = None
                else:
                    containercase.product = None
                containercase.save()

            else:
                containercase = ContainerCase.objects.create(
                    name=containercase_form.cleaned_data['name'],
                    shop=self.shop
                )
                if containercase_form.cleaned_data['base_container']:
                    try:
                        containercase.product = Container.objects.filter(
                            product_base=new_base,
                            is_sold=False)[0]
                    except KeyError:
                        containercase.product = None
                containercase.save()

        return super(ShopContainerCases, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'url_shop_containercases',
            kwargs={'group_name': self.group.name}
        )
