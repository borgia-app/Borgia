from django.conf.urls import url

from finances.views import *


urlpatterns = [
    # Model Transaction
    url(r'^transaction/create/$', TransactionCreateView.as_view(), name='url_create_transaction'),  # C
    url(r'^transaction/validation/(?P<pk>\d+)/$', TransactionValidationView.as_view(),
        name='url_validation_transaction'),  # Validation
    url(r'^transaction/retrieve/(?P<pk>\d+)/$', TransactionRetrieveView.as_view(), name='url_retrieve_transaction'),  # R
    url(r'^transaction/update/(?P<pk>\d+)/$', TransactionUpdateView.as_view(), name='url_update_transaction'),  # U
    url(r'^transaction/delete/(?P<pk>\d+)/$', TransactionDeleteView.as_view(), name='url_delete_transaction'),  # D
    url(r'^transaction/$', TransactionListView.as_view(), name='url_list_transaction'),  # Liste

    # Model Cheque
    url(r'^cheque/create/$', ChequeCreateView.as_view(), name='url_create_cheque'),  # C
    url(r'^cheque/retrieve/(?P<pk>\d+)/$', ChequeRetrieveView.as_view(), name='url_retrieve_cheque'),  # R
    url(r'^cheque/update/(?P<pk>\d+)/$', ChequeUpdateView.as_view(), name='url_update_cheque'),  # U
    url(r'^cheque/delete/(?P<pk>\d+)/$', ChequeDeleteView.as_view(), name='url_delete_cheque'),  # D
    url(r'^cheque/$', ChequeListView.as_view(), name='url_list_cheque'),  # Liste

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

    url(r'^transaction/create_cheque_fast/$', TransactionChequeFastCreateView.as_view(),
        name='url_create_transaction_cheque_fast'),
    url(r'^transaction/create_cash_fast/$', TransactionCashFastCreateView.as_view(),
        name='url_create_transaction_cash_fast'),
    url(r'^transaction/create_lydia_fast/$', TransactionLydiaFastCreateView.as_view(),
        name='url_create_transaction_lydia_fast'),
]