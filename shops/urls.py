from django.conf.urls import url

from shops.views import *


urlpatterns = [
    # Model Shop
    url(r'^shop/create/$', ShopCreateView.as_view(), name='url_create_shop'),  # C
    url(r'^shop/retrieve/(?P<pk>\d+)/$', ShopRetrieveView.as_view(), name='url_retrieve_shop'),  # R
    url(r'^shop/update/(?P<pk>\d+)/', ShopUpdateView.as_view(), name='url_update_shop'),  # U
    url(r'^shop/delete/(?P<pk>\d+)/$', ShopDeleteView.as_view(), name='url_delete_shop'),  # D
    url(r'^shop/list/$', ShopListView.as_view(), name='url_list_shop'),  # L

    # Model Single Product
    url(r'^singleproduct/create/$', SingleProductCreateView.as_view(), name='url_create_singleproduct'),  # C
    url(r'^singleproduct/retrieve/(?P<pk>\d+)/$', SingleProductRetrieveView.as_view(), name='url_retrieve_singleproduct'),  # R
    url(r'^singleproduct/update/(?P<pk>\d+)/', SingleProductUpdateView.as_view(), name='url_update_singleproduct'),  # U
    url(r'^singleproduct/delete/(?P<pk>\d+)/$', SingleProductDeleteView.as_view(), name='url_delete_singleproduct'),  # D
    url(r'^singleproduct/list/$', SingleProductListView.as_view(), name='url_list_singleproduct'),  # L

    # Model Container
    url(r'^container/create/$', ContainerCreateView.as_view(), name='url_create_container'),  # C
    url(r'^container/retrieve/(?P<pk>\d+)/$', ContainerRetrieveView.as_view(), name='url_retrieve_container'),  # R
    url(r'^container/update/(?P<pk>\d+)/', ContainerUpdateView.as_view(), name='url_update_container'),  # U
    url(r'^container/delete/(?P<pk>\d+)/$', ContainerDeleteView.as_view(), name='url_delete_container'),  # D
    url(r'^container/list/$', ContainerListView.as_view(), name='url_list_container'),  # L

    # Model Product Unit
    url(r'^productunit/create/$', ProductUnitCreateView.as_view(), name='url_create_productunit'),  # C
    url(r'^productunit/retrieve/(?P<pk>\d+)/$', ProductUnitRetrieveView.as_view(), name='url_retrieve_productunit'),  # R
    url(r'^productunit/update/(?P<pk>\d+)/', ProductUnitUpdateView.as_view(), name='url_update_productunit'),  # U
    url(r'^productunit/delete/(?P<pk>\d+)/$', ProductUnitDeleteView.as_view(), name='url_delete_productunit'),  # D
    url(r'^productunit/list/$', ProductUnitListView.as_view(), name='url_list_productunit'),  # L
]