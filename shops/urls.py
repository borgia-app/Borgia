#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from shops.views import *


urlpatterns = [
    # Models
    url(r'^singleproduct/create/multiple/$', permission_required('shops.add_singleproduct', raise_exception=True)
    (SingleProductCreateMultipleView.as_view()), name='url_create_singleproduct_multiple'),  # C multiple
    url(r'^singleproduct/retrieve/(?P<pk>\d+)/$', permission_required('shops.retrieve_singleproduct', raise_exception=True)
    (SingleProductRetrieveView.as_view()), name='url_retrieve_singleproduct'),  # R
    url(r'^singleproduct/$', permission_required('shops.list_singleproduct', raise_exception=True)
    (SingleProductListView.as_view()), name='url_list_singleproduct'),  # L
    url(r'^container/create/multiple/$', permission_required('shops.add_container', raise_exception=True)
    (ContainerCreateMultipleView.as_view()), name='url_create_container_multiple'),  # C multiple
    url(r'^container/retrieve/(?P<pk>\d+)/$', permission_required('shops.retrieve_singleproduct', raise_exception=True)
    (ContainerRetrieveView.as_view()), name='url_retrieve_container'),  # R
    url(r'^container/$', permission_required('shops.list_singleproduct', raise_exception=True)
    (ContainerListView.as_view()), name='url_list_container'),  # L
    url(r'^productunit/create/$', permission_required('shops.add_productunit', raise_exception=True)
    (ProductUnitCreateView.as_view()), name='url_create_productunit'),  # C
    url(r'^productunit/retrieve/(?P<pk>\d+)/$', permission_required('shops.retrieve_singleproduct', raise_exception=True)
    (ProductUnitRetrieveView.as_view()), name='url_retrieve_productunit'),  # R
    url(r'^productunit/update/(?P<pk>\d+)/$', permission_required('shops.update_singleproduct', raise_exception=True)
    (ProductUnitUpdateView.as_view()), name='url_update_productunit'),  # U
    url(r'^productunit/delete/(?P<pk>\d+)/$', permission_required('shops.delete_singleproduct', raise_exception=True)
    (ProductUnitDeleteView.as_view()), name='url_delete_productunit'),  # D
    url(r'^productunit/$', permission_required('shops.list_singleproduct', raise_exception=True)
    (ProductUnitListView.as_view()), name='url_list_productunit'),  # L
    url(r'^productbase/create/$', permission_required('shops.add_productbase', raise_exception=True)
    (ProductBaseCreateView.as_view()), name='url_create_productbase'),  # C
    url(r'^productbase/retrieve/(?P<pk>\d+)/$', permission_required('shops.retrieve_singleproduct', raise_exception=True)
    (ProductBaseRetrieveView.as_view()), name='url_retrieve_productbase'),  # C
    url(r'^productbase/update/(?P<pk>\d+)/$', permission_required('shops.update_singleproduct', raise_exception=True)
    (ProductBaseUpdateView.as_view()), name='url_update_productbase'),  # C
    url(r'^productbase/delete/(?P<pk>\d+)/$', permission_required('shops.delete_singleproduct', raise_exception=True)
    (ProductBaseDeleteView.as_view()), name='url_delete_productbase'),  # C
    url(r'^productbase/$', permission_required('shops.list_singleproduct', raise_exception=True)
    (ProductBaseListView.as_view()), name='url_list_productbase'),  # C

    # Foyer
    url(r'^foyer/consumption/$', PurchaseFoyer.as_view(), name='url_purchase_foyer'),
    url(r'^foyer/workboard$', permission_required('shops.reach_workboard_foyer', raise_exception=True)
    (workboard_foyer), name='url_workboard_foyer'),
    url(r'^foyer/replacement_keg', permission_required('shops.change_active_keg', raise_exception=True)
    (ReplacementActiveKeyView.as_view()), name='url_replacement_active_keg'),
    # Auberge
    url(r'^auberge/consumption/$', permission_required('shops.sell_auberge', raise_exception=True)
    (PurchaseAuberge.as_view()), name='url_purchase_auberge'),
    url(r'^auberge/workboard', permission_required('shops.reach_workboard_auberge')
    (workboard_auberge), name='url_workboard_foyer'),
]