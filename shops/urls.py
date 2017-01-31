#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from shops.views import *


urlpatterns = [

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
