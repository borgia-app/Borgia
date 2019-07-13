from django.urls import include, path

from finances.views import (ExceptionnalMovementList,
                            ExceptionnalMovementRetrieve, RechargingCreate,
                            RechargingList, RechargingRetrieve,
                            SelfLydiaConfirm, SelfLydiaCreate,
                            SelfTransactionList, TransfertCreate,
                            TransfertList, TransfertRetrieve,
                            UserExceptionnalMovementCreate,
                            self_lydia_callback)

finances_patterns = [
    path('finances/', include([
        path('transactions/', SelfTransactionList.as_view(),
             name='url_self_transaction_list'),
        # TO USERS
        path('users/<int:user_pk>/', include([
            path('exceptionnal_movement/create/', UserExceptionnalMovementCreate.as_view(),
                 name='url_user_exceptionnalmovement_create'),
            path('rechargings/create', RechargingCreate.as_view(),
                 name='url_recharging_create')
        ])),
        # RECHARGINGS
        path('rechargings/', include([
            path('', RechargingList.as_view(), name='url_recharging_list'),
            path('<int:recharging_pk>/', RechargingRetrieve.as_view(),
                 name='url_recharging_retrieve')
        ])),
        # TRANSFERTS
        path('transferts/', include([
            path('', TransfertList.as_view(), name='url_transfert_list'),
            path('create/', TransfertCreate.as_view(),
                 name='url_transfert_create'),
            path('<int:transfert_pk>/', TransfertRetrieve.as_view(),
                 name='url_transfert_retrieve')
        ])),
        # EXCEPTIONNAL MOVEMENTS
        path('exceptionnal_movements/', include([
            path('', ExceptionnalMovementList.as_view(),
                 name='url_exceptionnalmovement_list'),
            path('<int:exceptionnalmovement_pk>/', ExceptionnalMovementRetrieve.as_view(),
                 name='url_exceptionnalmovement_retrieve')
        ])),
        # Lydias
        path('lydias/', include([
            path('callback/', self_lydia_callback,
                 name='url_self_lydia_callback'),
            path('create/', SelfLydiaCreate.as_view(),
                 name='url_self_lydia_create'),
            path('confirm/', SelfLydiaConfirm.as_view(),
                 name='url_self_lydia_confirm')
        ]))
    ]))
]
