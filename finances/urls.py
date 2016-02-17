#-*- coding: utf-8 -*-
from django.conf.urls import url

from finances.views import *


urlpatterns = [

    # Model Cheque
    url(r'^cheque/create/$', ChequeCreateView.as_view(), name='url_create_cheque'),  # C
    url(r'^cheque/retrieve/(?P<pk>\d+)/$', ChequeRetrieveView.as_view(), name='url_retrieve_cheque'),  # R
    url(r'^cheque/update/(?P<pk>\d+)/$', ChequeUpdateView.as_view(), name='url_update_cheque'),  # U
    url(r'^cheque/delete/(?P<pk>\d+)/$', ChequeDeleteView.as_view(), name='url_delete_cheque'),  # D
    url(r'^cheque/$', ChequeListView.as_view(), name='url_list_cheque'),  # Liste

    # Model Bank Account
    url(r'^bank_account/create/$', BankAccountCreateView.as_view(), name='url_create_bank_account'),  # C
    url(r'^bank_account/update/(?P<pk>\d+)/$', BankAccountUpdateView.as_view(), name='url_update_bank_account'),  # U
    url(r'^bank_account/delete/(?P<pk>\d+)/$', BankAccountDeleteView.as_view(), name='url_delete_bank_account'),  # D
    url(r'^bank_account/$', BankAccountListView.as_view(), name='url_list_bank_account'),  # Liste
    url(r'^bank_account_from_user/$', bank_account_from_user, name='url_bank_account_from_user'),

    # Model Cash
    url(r'^cash/create/$', CashCreateView.as_view(), name='url_create_cash'),  # C
    url(r'^cash/retrieve/(?P<pk>\d+)/$', CashRetrieveView.as_view(), name='url_retrieve_cash'),  # R
    url(r'^cash/update/(?P<pk>\d+)/$', CashUpdateView.as_view(), name='url_update_cash'),  # U
    url(r'^cash/delete/(?P<pk>\d+)/$', CashDeleteView.as_view(), name='url_delete_cash'),  # D
    url(r'^cash/$', CashListView.as_view(), name='url_list_cash'),  # Liste

    # Model Lydia
    url(r'^lydia/create/$', LydiaCreateView.as_view(), name='url_create_lydia'),  # C
    url(r'^lydia/retrieve/(?P<pk>\d+)/$', LydiaRetrieveView.as_view(), name='url_retrieve_lydia'),  # R
    url(r'^lydia/update/(?P<pk>\d+)/$', LydiaUpdateView.as_view(), name='url_update_lydia'),  # U
    url(r'^lydia/delete/(?P<pk>\d+)/$', LydiaDeleteView.as_view(), name='url_delete_lydia'),  # D
    url(r'^lydia/$', LydiaListView.as_view(), name='url_list_lydia'),  # Liste

    # Model Sale
    url(r'^sale/retrieve/(?P<pk>\d+)/$', SaleRetrieveView.as_view(), name='url_retrieve_sale'),  # R
    url(r'^sale/$', SaleListView.as_view(), name='url_list_sale'),  # Liste

    # Supply
    url(r'^supply/cheque/$', SupplyChequeView.as_view(), name='url_supply_cheque'),
]