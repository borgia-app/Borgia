#-*- coding: utf-8 -*-
from django.conf.urls import url

from finances.views import *


urlpatterns = [
    # Models
    url(r'^cheque/retrieve/(?P<pk>\d+)/$', ChequeRetrieveView.as_view(), name='url_retrieve_cheque'),  # R
    url(r'^cheque/$', ChequeListView.as_view(), name='url_list_cheque'),  # Liste
    url(r'^bank_account/create/$', BankAccountCreateView.as_view(), name='url_create_bank_account'),  # C
    url(r'^bank_account/update/(?P<pk>\d+)/$', BankAccountUpdateView.as_view(), name='url_update_bank_account'),  # U
    url(r'^bank_account/delete/(?P<pk>\d+)/$', BankAccountDeleteView.as_view(), name='url_delete_bank_account'),  # D
    url(r'^bank_account/$', BankAccountListView.as_view(), name='url_list_bank_account'),  # Liste
    url(r'^bank_account_from_user/$', bank_account_from_user, name='url_bank_account_from_user'),
    url(r'^cash/retrieve/(?P<pk>\d+)/$', CashRetrieveView.as_view(), name='url_retrieve_cash'),  # R
    url(r'^cash/$', CashListView.as_view(), name='url_list_cash'),  # Liste
    url(r'^lydia/retrieve/(?P<pk>\d+)/$', LydiaRetrieveView.as_view(), name='url_retrieve_lydia'),  # R
    url(r'^lydia/$', LydiaListView.as_view(), name='url_list_lydia'),  # Liste
    url(r'^sale/retrieve/(?P<pk>\d+)/$', SaleRetrieveView.as_view(), name='url_retrieve_sale'),  # R
    url(r'^sale/$', SaleListView.as_view(), name='url_list_sale'),  # Liste

    # Supply
    url(r'^supply/cheque/$', SupplyChequeView.as_view(), name='url_supply_cheque'),
    url(r'^supply/cash/$', SupplyCashView.as_view(), name='url_supply_cash'),
    url(r'^supply/lydia/$', SupplyLydiaView.as_view(), name='url_supply_lydia'),
]
