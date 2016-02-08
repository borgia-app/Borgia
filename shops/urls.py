#-*- coding: utf-8 -*-
from django.conf.urls import url

from shops.views import *


urlpatterns = [
    # Model Shop
    url(r'^shop/create/$', ShopCreateView.as_view(), name='url_create_shop'),  # C
    url(r'^shop/retrieve/(?P<pk>\d+)/$', ShopRetrieveView.as_view(), name='url_retrieve_shop'),  # R
    url(r'^shop/update/(?P<pk>\d+)/$', ShopUpdateView.as_view(), name='url_update_shop'),  # U
    url(r'^shop/delete/(?P<pk>\d+)/$', ShopDeleteView.as_view(), name='url_delete_shop'),  # D
    url(r'^shop/$', ShopListView.as_view(), name='url_list_shop'),  # L

    # Model Single Product
    url(r'^singleproduct/create/$', SingleProductCreateView.as_view(), name='url_create_singleproduct'),  # C
    url(r'^singleproduct/retrieve/(?P<pk>\d+)/$', SingleProductRetrieveView.as_view(), name='url_retrieve_singleproduct'),  # R
    url(r'^singleproduct/update/(?P<pk>\d+)/$', SingleProductUpdateView.as_view(), name='url_update_singleproduct'),  # U
    url(r'^singleproduct/delete/(?P<pk>\d+)/$', SingleProductDeleteView.as_view(), name='url_delete_singleproduct'),  # D
    url(r'^singleproduct/$', SingleProductListView.as_view(), name='url_list_singleproduct'),  # L

    # Model Container
    url(r'^container/create/$', ContainerCreateView.as_view(), name='url_create_container'),  # C
    url(r'^container/retrieve/(?P<pk>\d+)/$', ContainerRetrieveView.as_view(), name='url_retrieve_container'),  # R
    url(r'^container/update/(?P<pk>\d+)/$', ContainerUpdateView.as_view(), name='url_update_container'),  # U
    url(r'^container/delete/(?P<pk>\d+)/$', ContainerDeleteView.as_view(), name='url_delete_container'),  # D
    url(r'^container/$', ContainerListView.as_view(), name='url_list_container'),  # L

    # Model Product Unit
    url(r'^productunit/create/$', ProductUnitCreateView.as_view(), name='url_create_productunit'),  # C
    url(r'^productunit/retrieve/(?P<pk>\d+)/$', ProductUnitRetrieveView.as_view(), name='url_retrieve_productunit'),  # R
    url(r'^productunit/update/(?P<pk>\d+)/$', ProductUnitUpdateView.as_view(), name='url_update_productunit'),  # U
    url(r'^productunit/delete/(?P<pk>\d+)/$', ProductUnitDeleteView.as_view(), name='url_delete_productunit'),  # D
    url(r'^productunit/$', ProductUnitListView.as_view(), name='url_list_productunit'),  # L

    # Model Tap
    url(r'^tap/create/$', TapCreateView.as_view(), name='url_create_tap'),  # C
    url(r'^tap/retrieve/(?P<pk>\d+)/$', TapRetrieveView.as_view(), name='url_retrieve_tap'),  # C
    url(r'^tap/update/(?P<pk>\d+)/$', TapUpdateView.as_view(), name='url_update_tap'),  # C
    url(r'^tap/delete/(?P<pk>\d+)/$', TapDeleteView.as_view(), name='url_delete_tap'),  # C
    url(r'^tap/$', TapListView.as_view(), name='url_list_tap'),  # C

    # Consommation foyer
    url(r'^foyer/consumption/$', purchase_foyer, name='url_purchase_foyer'),

    # Workboard
    url(r'^workboard/foyer$', workboard_foyer, name='url_workboard_foyer'),
]