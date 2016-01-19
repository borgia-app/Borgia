from django.shortcuts import render, HttpResponseRedirect, force_text, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.views.generic import ListView, DetailView, FormView
from shops.models import *


# Model SHOP
# C
class ShopCreateView(CreateView):
    model = Shop
    fields = ['name', 'description']
    template_name = 'shops/shop_create.html'
    success_url = '/auth/login'


# R
class ShopRetrieveView(DetailView):
    model = Shop
    template_name = 'shops/shop_retrieve.html'


# U
class ShopUpdateView(UpdateView):
    model = Shop
    fields = ['name', 'description']
    template_name = 'shops/shop_update.html'
    success_url = '/auth/login'


# D
class ShopDeleteView(DeleteView):
    model = Shop
    template_name = 'shops/shop_delete.html'
    success_url = '/auth/login'


# List
class ShopListView(ListView):
    model = Shop
    template_name = 'shops/shop_list.html'
    queryset = Shop.objects.all()


# Model SINGLEPRODUCT
# C
class SingleProductCreateView(CreateView):
    model = SingleProduct
    fields = ['name', 'description', 'price']
    template_name = 'shops/singleproduct_create.html'
    success_url = '/auth/login'


# R
class SingleProductRetrieveView(DetailView):
    model = SingleProduct
    template_name = 'shops/singleproduct_retrieve.html'


# U
class SingleProductUpdateView(UpdateView):
    model = SingleProduct
    fields = ['name', 'description', 'is_available_for_sale', 'is_available_for_borrowing', 'peremption_date',
              'is_sold', 'price']
    template_name = 'shops/singleproduct_update.html'
    success_url = '/auth/login'


# D
class SingleProductDeleteView(DeleteView):
    model = SingleProduct
    template_name = 'shops/singleproduct_delete.html'
    success_url = '/auth/login'


# List
class SingleProductListView(ListView):
    model = SingleProduct
    template_name = 'shops/singleproduct_list.html'
    queryset = SingleProduct.objects.all()


# Model CONTAINER
# C
class ContainerCreateView(CreateView):
    model = Container
    fields = ['product_unit', 'initial_quantity', 'is_returnable', 'value_when_returned']
    template_name = 'shops/container_create.html'
    success_url = '/auth/login'


# R
class ContainerRetrieveView(DetailView):
    model = Container
    template_name = 'shops/container_retrieve.html'


# U
class ContainerUpdateView(UpdateView):
    model = Container
    fields = ['name', 'description', 'is_available_for_sale', 'is_available_for_borrowing', 'peremption_date',
              'product_unit', 'initial_quantity', 'is_returnable', 'value_when_returned']
    template_name = 'shops/container_update.html'
    success_url = '/auth/login'


# D
class ContainerDeleteView(DeleteView):
    model = Container
    template_name = 'shops/container_delete.html'
    success_url = '/auth/login'


# List
class ContainerListView(ListView):
    model = Container
    template_name = 'shops/container_list.html'
    queryset = Container.objects.all()


# Model PRODUCTUNIT
# C
class ProductUnitCreateView(CreateView):
    model = ProductUnit
    fields = ['name', 'description', 'price', 'unit', 'type']
    template_name = 'shops/productunit_create.html'
    success_url = '/auth/login'


# R
class ProductUnitRetrieveView(DetailView):
    model = ProductUnit
    template_name = 'shops/productunit_retrieve.html'


# U
class ProductUnitUpdateView(UpdateView):
    model = ProductUnit
    fields = ['name', 'description', 'price', 'unit', 'type']
    template_name = 'shops/productunit_update.html'
    success_url = '/auth/login'


# D
class ProductUnitDeleteView(DeleteView):
    model = ProductUnit
    template_name = 'shops/productunit_delete.html'
    success_url = '/auth/login'


# List
class ProductUnitListView(ListView):
    model = ProductUnit
    template_name = 'shops/productunit_list.html'
    queryset = ProductUnit.objects.all()