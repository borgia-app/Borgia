from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import (
    password_reset, password_reset_complete,
    password_reset_confirm, password_change, password_change_done,
    password_reset_done)
from borgia.views import (
    jsi18n_catalog, TestBootstrapSober,
    handler403, handler404, handler500,
    Login, Logout, GadzartsGroupWorkboard, ShopGroupWorkboard,
    PresidentsGroupWorkboard, VicePresidentsInternalGroupWorkboard,
    TreasurersGroupWorkboard
    )
from django.conf import settings
from django.conf.urls.static import static

from users.views import *
from shops.views import (
    ProductList, ProductCreate, ProductDeactivate, ProductRetrieve,
    ProductUpdate, ShopCreate, ShopList, ShopUpdate,
    ProductUpdatePrice, ShopCheckup
    )
from shops.models import Product
from finances.views import *
from modules.views import *
from notifications.views import *
from stocks.views import *
from api.Schema.main import schema
from graphene_django.views import GraphQLView
from api.views import AuthGenerateJWT, AuthVerifyJWT, AuthInvalidateJWT, GraphQLJwtProtectedView

handler403 = handler403
handler404 = handler404
handler500 = handler500

urlpatterns = [
    url(r'^self/lydias/callback/$',
        self_lydia_callback,
        name='url_self_lydia_callback'),

    # GraphQL endpoint
    url(r'^graphql', GraphQLJwtProtectedView.as_view(graphiql=True, schema=schema)),
    # JWT auth backend
    url(r'^jwt/new.json$', AuthGenerateJWT.as_view()),
    url(r'^jwt/token/(?P<token>.+)/(?P<pk>\d+).json$', AuthVerifyJWT.as_view()),
    url(r'^jwt/invalidate/(?P<token>.+)/(?P<pk>\d+).json$', AuthInvalidateJWT.as_view()),

        #####################
        #     WORKBOARDS    #
        #####################
    url(r'^presidents/$',
        PresidentsGroupWorkboard.as_view(), {'group_name': 'presidents'},
        name='url_group_workboard'),
    url(r'^presidents/workboard/$',
        PresidentsGroupWorkboard.as_view(), {'group_name': 'presidents'},
        name='url_group_workboard'),

    url(r'^vice-presidents-internal/$',
        VicePresidentsInternalGroupWorkboard.as_view(), {'group_name': 'vice-presidents-internal'},
        name='url_group_workboard'),
    url(r'^vice-presidents-internal/workboard/$',
        VicePresidentsInternalGroupWorkboard.as_view(), {'group_name': 'vice-presidents-internal'},
        name='url_group_workboard'),

    url(r'^treasurers/$',
        TreasurersGroupWorkboard.as_view(), {'group_name': 'treasurers'},
        name='url_group_workboard'),
    url(r'^treasurers/workboard/$',
        TreasurersGroupWorkboard.as_view(), {'group_name': 'treasurers'},
        name='url_group_workboard'),

    url(r'^gadzarts/$',
        GadzartsGroupWorkboard.as_view(), {'group_name': 'gadzarts'},
        name='url_group_workboard'),
    url(r'^gadzarts/workboard/$',
        GadzartsGroupWorkboard.as_view(), {'group_name': 'gadzarts'},
        name='url_group_workboard'),

    url(r'^(?P<group_name>[\w-]+)/$',
        ShopGroupWorkboard.as_view(), name='url_group_workboard'),
    url(r'^(?P<group_name>[\w-]+)/workboard/$',
        ShopGroupWorkboard.as_view(), name='url_group_workboard'),

        #####################
        #       USERS       #
        #####################
    url(r'^(?P<group_name>[\w-]+)/users/create/$',
        UserCreateView.as_view(), name='url_user_create'),
    url(r'^(?P<group_name>[\w-]+)/users/$',
        UserListView.as_view(), name='url_user_list'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<pk>\d+)/$',
        UserRetrieveView.as_view(), name='url_user_retrieve'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<pk>\d+)/update/$',
        UserUpdateAdminView.as_view(), name='url_user_update'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<pk>\d+)/deactivate/$',
        UserDeactivateView.as_view(), name='url_user_deactivate'),

    url(r'^(?P<group_name>[\w-]+)/users/(?P<user_pk>\d+)/bank_accounts/create/$',
        UserBankAccountCreate.as_view(), name='url_user_bankaccount_create'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<user_pk>\d+)/bank_accounts/(?P<pk>\d+)/update/$',
        UserBankAccountUpdate.as_view(), name='url_user_bankaccount_update'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<user_pk>\d+)/bank_accounts/(?P<pk>\d+)/delete/$',
        UserBankAccountDelete.as_view(), name='url_user_bankaccount_delete'),

    url(r'^(?P<group_name>[\w-]+)/users/(?P<user_pk>\d+)/exceptionnal_movement/create/$',
        UserExceptionnalMovementCreate.as_view(), name='url_user_exceptionnalmovement_create'),
    url(r'^(?P<group_name>[\w-]+)/users/(?P<user_pk>\d+)/supply_money/$',
        UserSupplyMoney.as_view(), name='url_user_supplymoney'),


        #####################
        #      GROUPS       #
        #####################
    url(r'^(?P<group_name>[\w-]+)/groups/(?P<pk>\d+)/update/$',
        ManageGroupView.as_view(), name='url_group_update'),


        #####################
        #     PRODUCTS      #
        #####################
    url(r'^(?P<group_name>[\w-]+)/products/$',
        ProductList.as_view(), name='url_product_list'),
    url(r'^(?P<group_name>[\w-]+)/products/create/$',
        ProductCreate.as_view(), name='url_product_create'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/$',
        ProductRetrieve.as_view(), name='url_product_retrieve'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/update/$',
        ProductUpdate.as_view(), name='url_product_update'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/update/price/$',
        ProductUpdatePrice.as_view(), name='url_product_update_price'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/deactivate/$',
        ProductDeactivate.as_view(), name='url_product_deactivate'),

        #####################
        #      STOCKS       #
        #####################
    url(r'^(?P<group_name>[\w-]+)/stocks/entries/create/$',
        ShopStockEntryCreate.as_view(), name='url_stock_entry_create'),
    url(r'^(?P<group_name>[\w-]+)/stocks/entries/$',
        StockEntryList.as_view(), name='url_stock_entry_list'),
    url(r'^(?P<group_name>[\w-]+)/stocks/entries/(?P<pk>\d+)/$',
        StockEntryRetrieve.as_view(), name='url_stock_entry_retrieve'),
    url(r'^(?P<group_name>[\w-]+)/stocks/inventories/create/$',
        ShopInventoryCreate.as_view(), name='url_inventory_create'),
    url(r'^(?P<group_name>[\w-]+)/stocks/inventories/$',
        InventoryList.as_view(), name='url_inventory_list'),
    url(r'^(?P<group_name>[\w-]+)/stocks/inventories/(?P<pk>\d+)/$',
        InventoryRetrieve.as_view(), name='url_inventory_retrieve'),

        #####################
        #     FINANCES      #
        #####################
    url(r'^(?P<group_name>[\w-]+)/sales/$',
        SaleList.as_view(), name='url_sale_list'),
    url(r'^(?P<group_name>[\w-]+)/sales/(?P<pk>\d+)/$',
        SaleRetrieve.as_view(), name='url_sale_retrieve'),

    url(r'^(?P<group_name>[\w-]+)/rechargings/$',
        RechargingList.as_view(), name='url_recharging_list'),
    url(r'^(?P<group_name>[\w-]+)/rechargings/(?P<pk>\d+)/$',
        RechargingRetrieve.as_view(), name='url_recharging_retrieve'),

    url(r'^(?P<group_name>[\w-]+)/transferts/$',
        TransfertList.as_view(), name='url_transfert_list'),
    url(r'^(?P<group_name>[\w-]+)/transferts/(?P<pk>\d+)/$',
        TransfertRetrieve.as_view(), name='url_transfert_retrieve'),

    url(r'^(?P<group_name>[\w-]+)/exceptionnal_movements/$',
        ExceptionnalMovementList.as_view(),
        name='url_exceptionnalmovement_list'),
    url(r'^(?P<group_name>[\w-]+)/exceptionnal_movements/(?P<pk>\d+)/$',
        ExceptionnalMovementRetrieve.as_view(),
        name='url_exceptionnalmovement_retrieve'),

        #####################
        #      MODULES      #
        #####################
    url(r'^(?P<group_name>[\w-]+)/modules/self_sale/categories/create/$',
        ShopModuleCategoryCreate.as_view(),
        name='url_module_selfsale_categories_create',
        kwargs={'module_class': SelfSaleModule}),
    url(r'^(?P<group_name>[\w-]+)/modules/operator_sale/categories/create/$',
        ShopModuleCategoryCreate.as_view(),
        name='url_module_operatorsale_categories_create',
        kwargs={'module_class': OperatorSaleModule}),
    url(r'^(?P<group_name>[\w-]+)/modules/self_sale/categories/(?P<pk>\d+)/update/$',
        ShopModuleCategoryUpdate.as_view(),
        name='url_module_selfsale_categories_update',
        kwargs={'module_class': SelfSaleModule}),
    url(r'^(?P<group_name>[\w-]+)/modules/operator_sale/categories/(?P<pk>\d+)/update/$',
        ShopModuleCategoryUpdate.as_view(),
        name='url_module_operatorsale_categories_update',
        kwargs={'module_class': OperatorSaleModule}),
    url(r'^(?P<group_name>[\w-]+)/modules/self_sale/categories/(?P<pk>\d+)/delete/$',
        ShopModuleCategoryDelete.as_view(),
        name='url_module_selfsale_categories_delete',
        kwargs={'module_class': SelfSaleModule}),
    url(r'^(?P<group_name>[\w-]+)/modules/operator_sale/categories/(?P<pk>\d+)/delete/$',
        ShopModuleCategoryDelete.as_view(),
        name='url_module_operatorsale_categories_delete',
        kwargs={'module_class': OperatorSaleModule}),

    url(r'^(?P<group_name>[\w-]+)/modules/self_sale/$',
        SelfSaleShopModuleWorkboard.as_view(),
        name='url_module_selfsale_workboard'),
    url(r'^(?P<group_name>[\w-]+)/modules/operator_sale/$',
        OperatorSaleShopModuleWorkboard.as_view(),
        name='url_module_operatorsale_workboard'),

    url(r'^(?P<group_name>[\w-]+)/modules/self_sale/config/$',
        ShopModuleConfig.as_view(),
        name='url_module_selfsale_config',
        kwargs={'module_class': SelfSaleModule}),
    url(r'^(?P<group_name>[\w-]+)/modules/operator_sale/config/$',
        ShopModuleConfig.as_view(),
        name='url_module_operatorsale_config',
        kwargs={'module_class': OperatorSaleModule}),

    url(r'^(?P<group_name>[\w-]+)/(?P<shop_name>[\w-]+)/selfsale/$',
        SelfSaleShopModuleInterface.as_view(),
        name='url_module_selfsale'),
    url(r'^(?P<group_name>[\w-]+)/(?P<shop_name>[\w-]+)/operatorsale/$',
        OperatorSaleShopModuleInterface.as_view(),
        name='url_module_operatorsale'),


        #####################
        #   NOTIFICATIONS   #
        #####################
    url(r'^(?P<group_name>[\w-]+)/notifications/$',
        NotificationListCompleteView.as_view(),
        name='url_notification_list'),
    url(r'^ajax/notifications/read_notification/$',
        read_notification,
        name='url_read_notification'),
    url(r'^(?P<group_name>[\w-]+)/notifications/templates/$',
        NotificationTemplateListCompleteView.as_view(),
        name='url_notificationtemplate_list'),
    url(r'^(?P<group_name>[\w-]+)/notifications/templates/(?P<pk>\d+)/update/$',
        NotificationTemplateUpdateView.as_view(),
        name='url_notificationtemplate_change'),
    url(r'^(?P<group_name>[\w-]+)/notifications/templates/create(?:/(?P<notification_class>[a-zA-Z0-9_]+))?/$',
        NotificationTemplateCreateView.as_view(),
        name='url_notificationtemplate_create'),
    url(r'^(?P<group_name>[\w-]+)/notifications/templates/(?P<pk>\d+)/deactivate/$',
        NotificationTemplateDeactivateView.as_view(),
        name='url_notificationtemplate_deactivate'),
    url(r'^(?P<group_name>[\w-]+)/notifications/groups/$',
        NotificationGroupListCompleteView.as_view(),
        name='url_notificationgroup_list'),
    url(r'^(?P<group_name>[\w-]+)/notifications/groups/create/$',
        NotificationGroupCreateView.as_view(),
        name='url_notificationgroup_create'),
    url(r'^(?P<group_name>[\w-]+)/notifications/groups/(?P<pk>\d+)/update/$',
        NotificationGroupUpdateView.as_view(),
        name='url_notificationgroup_update'),


        #####################
        #       SHOPS       #
        #####################
    url(r'^(?P<group_name>[\w-]+)/shops/$',
        ShopList.as_view(),
        name='url_shop_list'),
    url(r'^(?P<group_name>[\w-]+)/shops/create/$',
        ShopCreate.as_view(),
        name='url_shop_create'),
    url(r'^(?P<group_name>[\w-]+)/shops/(?P<pk>\d+)/update/$',
        ShopUpdate.as_view(),
        name='url_shop_update'),
    url(r'^(?P<group_name>[\w-]+)/shops/(?P<pk>\d+)/checkup/$',
        ShopCheckup.as_view(),
        name='url_shop_checkup'),

        #####################
        #  SELF OPERATIONS  #
        #####################
    url(r'^(?P<group_name>[\w-]+)/self/transferts/create/$',
        SelfTransfertCreate.as_view(),
        name='url_self_transfert_create'),
    url(r'^(?P<group_name>[\w-]+)/users/self/$',
        SelfUserUpdate.as_view(),
        name='url_self_user_update'),
    url(r'^(?P<group_name>[\w-]+)/self/bank_accounts/create/$',
        SelfBankAccountCreate.as_view(),
        name='url_self_bankaccount_create'),
    url(r'^(?P<group_name>[\w-]+)/self/bank_accounts/(?P<pk>\d+)/update/$',
        SelfBankAccountUpdate.as_view(),
        name='url_self_bankaccount_update'),
    url(r'^(?P<group_name>[\w-]+)/self/bank_accounts/(?P<pk>\d+)/delete/$',
        SelfBankAccountDelete.as_view(),
        name='url_self_bankaccount_delete'),
    url(r'^(?P<group_name>[\w-]+)/self/sales/$',
        SelfTransactionList.as_view(),
        name='url_self_transaction_list'),

    url(r'^(?P<group_name>[\w-]+)/self/lydias/create/$',
        SelfLydiaCreate.as_view(),
        name='url_self_lydia_create'),
    url(r'^(?P<group_name>[\w-]+)/self/lydias/confirm/$',
        SelfLydiaConfirm.as_view(),
        name='url_self_lydia_confirm'),

        #####################
        #   SHAREDEVENTS    #
        #####################
    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/self_registration/$',
        SharedEventSelfRegistration.as_view(),
        name='url_sharedevent_self_registration'),

    url(r'^(?P<group_name>[\w-]+)/shared_events/create/$',
        SharedEventCreate.as_view(),
        name='url_sharedevent_create'),
    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/participants/(?P<user_pk>(\w|\d)+)/$',
        SharedEventRemoveUser.as_view(),
        name='url_sharedevent_remove_user'),
    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/update/$',
        SharedEventUpdate.as_view(),
        name='url_sharedevent_update'),
    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/delete/$',
        SharedEventDelete.as_view(),
        name='url_sharedevent_delete'),
    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/finish/$',
        SharedEventFinish.as_view(),
        name='url_sharedevent_finish'),
    url(r'^(?P<group_name>[\w-]+)/shared_events/$',
        SharedEventList.as_view(),
        name='url_sharedevent_list'),

    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/manage_users/$',
        SharedEventManageUsers.as_view(),
        name='url_sharedevent_manage_users'),
    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/change_weight/(?P<participant_pk>\d+)/$',
        SharedEventChangeWeight.as_view(),
        name='url_sharedevent_change_weight'),

    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/download_xlsx/$',
        SharedEventDownloadXlsx.as_view(),
        name='url_sharedevent_download_xlsx'),
    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/upload_xlsx/$',
        SharedEventUploadXlsx.as_view(),
        name='url_sharedevent_upload_xlsx'),


    url(r'^(?P<group_name>[\w-]+)/shared_events/(?P<pk>\d+)/proceed_payment/$',
        SharedEventProceedPayment.as_view(),
        name='url_sharedevent_proceed_payment'),

        #####################
        #   CONNECTIONS     #
        #####################
    url(r'^$', Login.as_view()),
    url(r'^auth/logout/',
        Logout.as_view(),
        name='url_logout'),

    url(r'^auth/login/$',
        Login.as_view(), {'save_login_url': False},
        name='url_login'),
    url(r'^auth/gadzarts/(?P<shop_name>[\w-]+)/$',
        Login.as_view(), {'save_login_url': True, 'gadzarts': True},
        name='url_login_direct_module_selfsale'),

    url(r'^auth/password_reset/$',
        password_reset,
        name='reset_password_reset1'),
    url(r'^auth/password_reset/done/$',
        password_reset_done,
        name='password_reset_done'),
    url(r'^auth/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^auth/done/$',
        password_reset_complete,
        name='password_reset_complete'),
    url(r'^auth/password_change/$',
        password_change, {'post_change_redirect': password_change_done},
        name='password_change'),
    url(r'^auth/password_change_done/$',
        password_change_done),

    url(r'^auth/(?P<shop_name>[\w-]+)/$',
        Login.as_view(), {'save_login_url': True, 'gadzarts': False},
        name='url_login_direct_module_operatorsale'),


    # Test Bootstrap CSS & components
    url('^tests/bootstrap$',
        TestBootstrapSober.as_view()),

    url(r'^ajax/username_from_username_part/$',
        username_from_username_part,
        name='url_ajax_username_from_username_part'),

    url(r'^admin/', admin.site.urls),
    url(r'^local/jsi18n$', jsi18n_catalog),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Cette ligne permet d'utiliser le dossier MEDIA en
# dev (en prod c'est automatique)
