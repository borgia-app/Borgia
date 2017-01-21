from django.core import serializers
from math import ceil

from django.shortcuts import render, force_text, HttpResponseRedirect, redirect
from django.shortcuts import HttpResponse, Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.auth import logout

from borgia.models import FormNextView, CreateNextView, UpdateNextView, ListCompleteView
from shops.models import *
from shops.forms import *
from users.models import User
from finances.models import *
from notifications.models import notify
from contrib.models import add_to_breadcrumbs
from borgia.utils import *


class ProductList(GroupPermissionMixin, ShopFromGroupMixin, View,
                  GroupLateralMenuMixin):
    template_name = 'shops/product_list.html'
    perm_codename = 'list_product'
    lm_active = 'lm_product_list'

    def get(self, request, *args, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context['product_list'] = ProductBase.objects.filter(shop=self.shop)
        return render(request, self.template_name, context=context)


class ProductCreate(GroupPermissionMixin, ShopFromGroupMixin, FormView,
                    GroupLateralMenuFormMixin):
    template_name = 'shops/product_create.html'
    perm_codename = 'add_product'
    lm_active = 'lm_product_create'
    form_class = ProductCreateForm

    def form_valid(self, form):
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
                                                       product_base=form.cleaned_data['product_base'])
        elif form.cleaned_data['product_base'].type == 'single_product':
            for i in range(0, form.cleaned_data['quantity']):
                product = SingleProduct.objects.create(price=form.cleaned_data['price'],
                                                       purchase_date=form.cleaned_data['purchase_date'],
                                                       expiry_date=form.cleaned_data['expiry_date'],
                                                       place=form.cleaned_data['place'],
                                                       product_base=form.cleaned_data['product_base'])
        return super(ProductCreate, self).form_valid(form)

    def get_initial(self):
        initial = super(ProductCreate, self).get_initial()
        initial['purchase_date'] = now
        return initial

    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        context['shop'] = self.shop
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

        return redirect(force_text(self.success_url))


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


class ProductUpdate(GroupPermissionMixin, ProductShopFromGroupMixin ,FormView,
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
