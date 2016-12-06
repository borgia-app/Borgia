#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from shops.views import *


urlpatterns = [
    # Models
    url(r'^product/create/multiple/(?P<shop>\w+)/$', permission_required('users.add_product', raise_exception=True)
    (ProductCreateMultipleView.as_view()), name='url_create_product_multiple'),
    url(r'^singleproduct/create/multiple/$', permission_required('shops.add_singleproduct', raise_exception=True)
    (SingleProductRetrieveView.as_view()), name='url_retrieve_singleproduct'),  # R
    url(r'^singleproduct/$', permission_required('shops.list_singleproduct', raise_exception=True)
    (SingleProductListView.as_view()), name='url_list_singleproduct'),  # L
    url(r'^container/create/multiple/$', permission_required('shops.add_container', raise_exception=True)
    (ContainerRetrieveView.as_view()), name='url_retrieve_container'),  # R
    url(r'^container/$', permission_required('shops.list_container', raise_exception=True)
    (ContainerListView.as_view()), name='url_list_container'),  # L
    url(r'^productunit/create/$', permission_required('shops.add_productunit', raise_exception=True)
    (ProductUnitCreateView.as_view()), name='url_create_productunit'),  # C
    url(r'^productunit/retrieve/(?P<pk>\d+)/$', permission_required('shops.retrieve_productunit', raise_exception=True)
    (ProductUnitRetrieveView.as_view()), name='url_retrieve_productunit'),  # R
    url(r'^productunit/update/(?P<pk>\d+)/$', permission_required('shops.change_productunit', raise_exception=True)
    (ProductUnitUpdateView.as_view()), name='url_update_productunit'),  # U
#    url(r'^productunit/delete/(?P<pk>\d+)/$', permission_required('shops.delete_productunit', raise_exception=True)
#    (ProductUnitDeleteView.as_view()), name='url_delete_productunit'),  # D
    url(r'^productunit/$', permission_required('shops.list_productunit', raise_exception=True)
    (ProductUnitListView.as_view()), name='url_list_productunit'),  # L
    url(r'^productbase/create/$', permission_required('shops.add_productbase', raise_exception=True)
    (ProductBaseCreateView.as_view()), name='url_create_productbase'),  # C
    url(r'^productbase/retrieve/(?P<pk>\d+)/$', permission_required('shops.retrieve_productbase', raise_exception=True)
    (ProductBaseRetrieveView.as_view()), name='url_retrieve_productbase'),  # C
    url(r'^productbase/update/(?P<pk>\d+)/$', permission_required('shops.change_productbase', raise_exception=True)
    (ProductBaseUpdateView.as_view()), name='url_update_productbase'),  # C
#    url(r'^productbase/delete/(?P<pk>\d+)/$', permission_required('shops.delete_productbase', raise_exception=True)
#    (ProductBaseDeleteView.as_view()), name='url_delete_productbase'),  # C
    url(r'^productbase/$', permission_required('shops.list_productbase', raise_exception=True)
    (ProductListView.as_view()), name='url_list_productbase'),  # C
    url(r'^product/$', permission_required('shops.list_productbase', raise_exception=True)
    (ProductListView.as_view()), name='url_list_product'),  # C

    # Foyer
    url(r'^foyer/consumption/$', PurchaseFoyer.as_view(), name='url_purchase_foyer'),
    url(r'^foyer/workboard$', permission_required('users.reach_workboard_foyer', raise_exception=True)
    (workboard_foyer), name='url_workboard_foyer'),
    url(r'^foyer/list_active_keg', permission_required('shops.change_active_keg', raise_exception=True)
    (list_active_keg), name='url_list_active_keg'),
    url(r'^foyer/replacement_keg', permission_required('shops.change_active_keg', raise_exception=True)
    (ReplacementActiveKeyView.as_view()), name='url_replacement_active_keg'),

    #Buquage Zifoys
    url(r'^foyer/debit/$', permission_required('shops.sell_foyer', raise_exception=True)
    (DebitZifoys.as_view()), name='url_debit_zifoys'),

    # Auberge
    url(r'^auberge/consumption/$', permission_required('shops.sell_auberge', raise_exception=True)
    (PurchaseAuberge.as_view()), name='url_purchase_auberge'),
    url(r'^auberge/workboard', permission_required('users.reach_workboard_auberge', raise_exception=True)
    (workboard_auberge), name='url_workboard_auberge'),

    #C-Vis
    url(r'^cvis/consumption/$', permission_required('shops.sell_cvis', raise_exception=True)
    (PurchaseCvis.as_view()), name='url_purchase_cvis'),
    url(r'^cvis/workboard', permission_required('users.reach_workboard_cvis', raise_exception=True)
    (workboard_cvis), name='url_workboard_cvis'),

    #Bkars
    url(r'^bkars/consumption/$', permission_required('shops.sell_bkars', raise_exception=True)
    (PurchaseBkars.as_view()), name='url_purchase_bkars'),
    url(r'^bkars/workboard', permission_required('users.reach_workboard_bkars', raise_exception=True)
    (workboard_bkars), name='url_workboard_bkars'),

]
