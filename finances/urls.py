#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from finances.views import *


urlpatterns = [
    # Models
    url(r'^cheque/retrieve/(?P<pk>\d+)/$', permission_required('finances.retrieve_cheque', raise_exception=True)
    (ChequeRetrieveView.as_view()), name='url_retrieve_cheque'),  # R
    url(r'^cheque/$', permission_required('finances.list_cheque', raise_exception=True)
    (ChequeListView.as_view()), name='url_list_cheque'),  # Liste
    url(r'^bank_account/create/$', permission_required('finances.add_bankaccount', raise_exception=True)
    (BankAccountCreateView.as_view()), name='url_create_bank_account'),  # C
    url(r'^bank_account/update/(?P<pk>\d+)/$', permission_required('finances.change_bankaccount', raise_exception=True)
    (BankAccountUpdateView.as_view()), name='url_update_bank_account'),  # U
    url(r'^bank_account/delete/(?P<pk>\d+)/$', permission_required('finances.delete_bankaccount', raise_exception=True)
    (BankAccountDeleteView.as_view()), name='url_delete_bank_account'),  # D
    url(r'^bank_account/$', permission_required('finances.list_bankaccount', raise_exception=True)
    (BankAccountListView.as_view()), name='url_list_bank_account'),  # Liste
    url(r'^bank_account_from_user/$', bank_account_from_user, name='url_bank_account_from_user'),
    url(r'^cash/retrieve/(?P<pk>\d+)/$', permission_required('finances.retrieve_cash', raise_exception=True)
    (CashRetrieveView.as_view()), name='url_retrieve_cash'),  # R
    url(r'^cash/$', permission_required('finances.list_cash', raise_exception=True)
    (CashListView.as_view()), name='url_list_cash'),  # Liste
    url(r'^lydia/retrieve/(?P<pk>\d+)/$', permission_required('finances.retrieve_lydia', raise_exception=True)
    (LydiaRetrieveView.as_view()), name='url_retrieve_lydia'),  # R
    url(r'^lydia/$', permission_required('finances.list_lydia', raise_exception=True)
    (LydiaListView.as_view()), name='url_list_lydia'),  # Liste
    url(r'^sale/retrieve/(?P<pk>\d+)/$', SaleRetrieveView.as_view(), name='url_retrieve_sale'),  # R
    url(r'^sale/$', permission_required('finances.list_sale', raise_exception=True)
    (SaleListView.as_view()), name='url_list_sale'),  # Liste

    # Supply
    url(r'^supply/cheque/$', permission_required('finances.add_cheque', raise_exception=True)
    (SupplyChequeView.as_view()), name='url_supply_cheque'),
    url(r'^supply/cash/$', permission_required('finances.add_cash', raise_exception=True)
    (SupplyCashView.as_view()), name='url_supply_cash'),
    url(r'^supply/lydia/$', permission_required('finances.add_lydia', raise_exception=True)
    (SupplyLydiaView.as_view()), name='url_supply_lydia'),

    # Transfert
    url(r'^transfert/create/$', permission_required('finances.add_transfert', raise_exception=True)
    (TransfertCreateView.as_view()), name='url_create_transfert'),

    # Trésorerie
    url(r'^treasury/workboard$', permission_required('users.reach_workboard_treasury', raise_exception=True)
    (workboard_treasury), name='url_workboard_treasury'),
]
