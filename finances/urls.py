#-*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from finances.views import *


urlpatterns = [
    # Models
    url(r'^bank_account/create/$', permission_required('finances.add_bankaccount', raise_exception=True)
    (BankAccountCreateView.as_view()), name='url_create_bank_account'),  # C
    url(r'^bank_account/create/own/$', permission_required('finances.add_own_bankaccount', raise_exception=True)
    (BankAccountCreateOwnView.as_view()), name='url_create_own_bank_account'),  # C
    url(r'^bank_account/update/(?P<pk>\d+)/$', BankAccountUpdateView.as_view(), name='url_update_bank_account'),  # U
    url(r'^bank_account/delete/(?P<pk>\d+)/$', BankAccountDeleteView.as_view(), name='url_delete_bank_account'),  # D
    url(r'^bank_account/$', permission_required('finances.list_bankaccount', raise_exception=True)
    (BankAccountListView.as_view()), name='url_list_bank_account'),  # Liste
    url(r'^bank_account_from_user/$', bank_account_from_user, name='url_bank_account_from_user'),
    url(r'^sale/retrieve/(?P<pk>\d+)/$', SaleRetrieveView.as_view(), name='url_retrieve_sale'),  # R
    url(r'^sale/(?P<organe>\w+)$', permission_required('finances.list_sale', raise_exception=True)
    (SaleListOrganeView.as_view()), name='url_list_sale_organe'),  # Liste Ventes par organe
    url(r'^sale/$', permission_required('finances.list_sale', raise_exception=True)
    (SaleListAllView.as_view()), name='url_list_sale_all'),  # Liste Ventes
    url(r'^shared_event/create/$', permission_required('finances.add_sharedevent', raise_exception=True)
    (SharedEventCreateView.as_view()), name='url_create_shared_event'),
    url(r'^shared_event/manage_list/$', permission_required('finances.manage_sharedevent', raise_exception=True)
    (SharedEventManageListView.as_view()), name='url_manage_list_shared_event'),
    url(r'^shared_event/list/$', permission_required('finances.list_sharedevent', raise_exception=True)
    (shared_event_list), name='url_list_shared_event'),
    url(r'^shared_event/registration/$', permission_required('finances.register_sharedevent', raise_exception=True)
    (shared_event_registration), name='url_registration_shared_event'),
    url(r'^shared_event/manage/(?P<pk>\d+)/$', SharedEventManageView.as_view(), name='url_manage_shared_event'),
    url(r'^shared_event/remove_participant/(?P<pk>\d+)/$', remove_participant_se, name='url_rm_participant_shared_event'),
    url(r'^shared_event/remvove_registered/(?P<pk>\d+)/$', remove_registered_se, name='url_rm_registered_shared_event'),
    url(r'^shared_event/change_ponderation/(?P<pk>\d+)/$', change_ponderation_se, name='url_change_ponderation_shared_event'),
    url(r'^shared_event/proceed_payment/(?P<pk>\d+)/$', permission_required('finances.proceed_payment_sharedevent', raise_exception=True)
    (proceed_payment_se), name='url_proceed_payment_shared_event'),
    url(r'^product_base/set_price/(?P<pk>\d+)/$', permission_required('shops.change_price_productbase', raise_exception=True)
    (SetPriceProductBaseView.as_view()), name='url_set_price_product_base'),

    # Supply
    url(r'^supply/united/$', permission_required('users.supply_account', raise_exception=True)
    (SupplyUnitedView.as_view()), name='url_supply_united'),
    url(r'^supply/lydia/self/$', SupplyLydiaSelfView.as_view(), name='url_supply_lydia_self'),
    url(r'^supply/lydia/self/confirm$', SupplyLydiaSelfConfirmView.as_view(), name='url_supply_lydia_self_confirm'),
    url(r'^supply/lydia/self/callback$', supply_lydia_self_callback, name='url_supply_lydia_self_callback'),
    url(r'^supply/exceptionnal$', permission_required('users.exceptionnal_movement', raise_exception=True)
    (ExceptionnalMovementView.as_view()), name='url_supply_exceptionnal'),

    # Transfert
    url(r'^transfert/create/$', permission_required('finances.add_transfert', raise_exception=True)
    (TransfertCreateView.as_view()), name='url_create_transfert'),

    # Trésorerie
    url(r'^treasury/workboard$', permission_required('users.reach_workboard_treasury', raise_exception=True)
    (workboard_treasury), name='url_workboard_treasury'),
    url(r'^treasury/retrieve_money', RetrieveMoneyView.as_view(), name='url_treasury_retrieve_money'),
]
