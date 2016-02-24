#-*- coding: utf-8 -*-
from django.conf.urls import url

from shops.views import *


urlpatterns = [
    # Models
    url(r'^singleproduct/create/multiple/$', SingleProductCreateMultipleView.as_view(),
        name='url_create_singleproduct_multiple'),  # C multiple
    url(r'^singleproduct/retrieve/(?P<pk>\d+)/$', SingleProductRetrieveView.as_view(), name='url_retrieve_singleproduct'),  # R
    url(r'^singleproduct/$', SingleProductListView.as_view(), name='url_list_singleproduct'),  # L
    url(r'^container/create/multiple/$', ContainerCreateMultipleView.as_view(),
        name='url_create_container_multiple'),  # C multiple
    url(r'^container/retrieve/(?P<pk>\d+)/$', ContainerRetrieveView.as_view(), name='url_retrieve_container'),  # R
    url(r'^container/$', ContainerListView.as_view(), name='url_list_container'),  # L
    url(r'^productunit/create/$', ProductUnitCreateView.as_view(), name='url_create_productunit'),  # C
    url(r'^productunit/retrieve/(?P<pk>\d+)/$', ProductUnitRetrieveView.as_view(), name='url_retrieve_productunit'),  # R
    url(r'^productunit/update/(?P<pk>\d+)/$', ProductUnitUpdateView.as_view(), name='url_update_productunit'),  # U
    url(r'^productunit/delete/(?P<pk>\d+)/$', ProductUnitDeleteView.as_view(), name='url_delete_productunit'),  # D
    url(r'^productunit/$', ProductUnitListView.as_view(), name='url_list_productunit'),  # L
    url(r'^productbase/create/$', ProductBaseCreateView.as_view(), name='url_create_productbase'),  # C
    url(r'^productbase/retrieve/(?P<pk>\d+)/$', ProductBaseRetrieveView.as_view(), name='url_retrieve_productbase'),  # C
    url(r'^productbase/update/(?P<pk>\d+)/$', ProductBaseUpdateView.as_view(), name='url_update_productbase'),  # C
    url(r'^productbase/delete/(?P<pk>\d+)/$', ProductBaseDeleteView.as_view(), name='url_delete_productbase'),  # C
    url(r'^productbase/$', ProductBaseListView.as_view(), name='url_list_productbase'),  # C

    # Foyer
    url(r'^foyer/consumption/$', purchase_foyer, name='url_purchase_foyer'),
    url(r'^foyer/workboard$', workboard_foyer, name='url_workboard_foyer'),
    url(r'^foyer/replacement_keg', ReplacementActiveKeyView.as_view(), name='url_replacement_active_keg'),
]