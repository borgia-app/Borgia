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
    url(r'^shared_event/create/$', permission_required('finances.add_sharedevent', raise_exception=True)
    (SharedEventCreateView.as_view()), name='url_create_shared_event'),
    url(r'^shared_event/update/$', permission_required('finances.change_sharedevent', raise_exception=True)
    (SharedEventUpdateView.as_view()), name='url_update_shared_event'),
    url(r'^shared_event/manage_list/$', permission_required('finances.manage_sharedevent', raise_exception=True)
    (SharedEventManageListView.as_view()), name='url_manage_list_shared_event'),
    url(r'^shared_event/list/$', permission_required('finances.list_sharedevent', raise_exception=True)
    (shared_event_list), name='url_list_shared_event'),
    url(r'^shared_event/registration/$', permission_required('finances.register_sharedevent', raise_exception=True)
    (shared_event_registration), name='url_registration_shared_event'),
    url(r'^shared_event/download_csv_user', DownloadCsvUserView.as_view(), name='url_shared_event_download_csv_user'),

    # Supply
    url(r'^supply/united/$', permission_required('users.supply_account', raise_exception=True)
    (SupplyUnitedView.as_view()), name='url_supply_united'),

    # Transfert
    url(r'^transfert/create/$', permission_required('finances.add_transfert', raise_exception=True)
    (TransfertCreateView.as_view()), name='url_create_transfert'),

    # Trésorerie
    url(r'^treasury/workboard$', permission_required('users.reach_workboard_treasury', raise_exception=True)
    (workboard_treasury), name='url_workboard_treasury'),
    url(r'^treasury/retrieve_money', RetrieveMoneyView.as_view(), name='url_treasury_retrieve_money'),

    # Requetes
    url(r'^electrovanne/request1$', electrovanne_request1, name='url_electrovanne_request1'),
    url(r'^electrovanne/request2$', electrovanne_request2, name='url_electrovanne_request2'),
    url(r'^electrovanne/date$', electrovanne_date, name='url_electrovanne_date'),
]
