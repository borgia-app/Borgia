from django.urls import include, path

from finances.views import (ExceptionnalMovementList,
                            ExceptionnalMovementRetrieve, RechargingList,
                            RechargingRetrieve, SaleList, SaleRetrieve,
                            SelfLydiaConfirm, SelfLydiaCreate,
                            SelfTransactionList, SelfTransfertCreate,
                            SharedEventChangeWeight, SharedEventCreate,
                            SharedEventDelete, SharedEventDownloadXlsx,
                            SharedEventFinish, SharedEventList,
                            SharedEventManageUsers, SharedEventRemoveUser,
                            SharedEventSelfRegistration, SharedEventUpdate,
                            SharedEventUploadXlsx, TransfertList,
                            TransfertRetrieve, UserExceptionnalMovementCreate,
                            UserSupplyMoney, self_lydia_callback)


finances_patterns = [
    path('<str:group_name>/', include([
        # TO USERS
        path('users/<int:user_pk>/', include([
            path('exceptionnal_movement/create/', UserExceptionnalMovementCreate.as_view(), name='url_user_exceptionnalmovement_create'),
            path('supply_money', UserSupplyMoney.as_view(), name='url_user_supplymoney')
        ])),
        # SALES
        path('sales/', include([
            path('', SaleList.as_view(), name='url_sale_list'),
            path('<int:pk>/', SaleRetrieve.as_view(), name='url_sale_retrieve')
        ])),
        # RECHARGINGS
        path('rechargings/', include([
            path('', RechargingList.as_view(), name='url_recharging_list'),
            path('<int:pk>/', RechargingRetrieve.as_view(), name='url_recharging_retrieve')
        ])),
        # TRANSFERTS
        path('transferts/', include([
            path('', TransfertList.as_view(), name='url_transfert_list'),
            path('<int:pk>/', TransfertRetrieve.as_view(), name='url_transfert_retrieve')
        ])),
        # EXCEPTIONNAL MOVEMENTS
        path('exceptionnal_movements/', include([
            path('', ExceptionnalMovementList.as_view(), name='url_exceptionnalmovement_list'),
            path('<int:pk>/', ExceptionnalMovementRetrieve.as_view(), name='url_exceptionnalmovement_retrieve')
        ])),
        # SELF OPERATIONS
        path('self/', include([
            path('transferts/create/', SelfTransfertCreate.as_view(), name='url_self_transfert_create'),
            path('transaction/', SelfTransactionList.as_view(), name='url_self_transaction_list'),
            path('lydias/create/', SelfLydiaCreate.as_view(), name='url_self_lydia_create'),
            path('lydias/confirm/', SelfLydiaConfirm.as_view(), name='url_self_lydia_confirm')
        ])),
        # SHARED EVENTS
        path('shared_events/', include([
            path('', SharedEventList.as_view(), name='url_sharedevent_list'),
            path('create/', SharedEventCreate.as_view(), name='url_sharedevent_create'),
            path('<int:pk>/', include([
                path('update/', SharedEventUpdate.as_view(), name='url_sharedevent_update'),
                path('delete/', SharedEventDelete.as_view(), name='url_sharedevent_delete'),
                path('finish/', SharedEventFinish.as_view(), name='url_sharedevent_finish'),
                path('remove/', SharedEventFinish.as_view(), name='url_sharedevent_finish'),
                path('self_registration/', SharedEventSelfRegistration.as_view(), name='url_sharedevent_self_registration'),
                path('users/', SharedEventManageUsers.as_view(), name='url_sharedevent_manage_users'),
                path('users/<int:user_pk>/remove/', SharedEventRemoveUser.as_view(), name='url_sharedevent_remove_user'),
                path('users/<int:user_pk>/change_weight', SharedEventChangeWeight.as_view(), name='url_sharedevent_change_weight'),
                path('xlsx/download/', SharedEventDownloadXlsx.as_view(), name='url_sharedevent_download_xlsx'),
                path('xlsx/upload/', SharedEventUploadXlsx.as_view(), name='url_sharedevent_upload_xlsx')
            ]))
        ]))
    ])),
    path('self/lydias/callback/', self_lydia_callback, name='url_self_lydia_callback')
]