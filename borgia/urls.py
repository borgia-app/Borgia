from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import logout, login, password_reset, password_reset_complete, password_reset_confirm,\
    password_change, password_change_done, password_reset_done
from borgia.views import (
    page_clean, jsi18n_catalog, TestBootstrapSober, GroupWorkboard,
    get_list_model, get_unique_model, handler403, handler404, handler500
    )
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.decorators import permission_required

from users.views import *
from shops.views import (
    ProductList, ProductCreate, ProductDeactivate, ProductRetrieve,
    ProductUpdate, PurchaseFoyer, ShopCreate, ShopList
    )
from shops.models import ProductBase, ProductUnit
from finances.views import *
from modules.views import *

handler403 = handler403
handler404 = handler404
handler500 = handler500

urlpatterns = [
    url(r'^(?P<group_name>[\w-]+)/$',
        GroupWorkboard.as_view(), name='url_group_workboard'),
    url(r'^(?P<group_name>[\w-]+)/workboard/$',
        GroupWorkboard.as_view(), name='url_group_workboard'),

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

    url(r'^(?P<group_name>[\w-]+)/users/link_token/$',
        LinkTokenUserView.as_view(), name='url_user_link_token'),
    url(r'^(?P<group_name>[\w-]+)/groups/(?P<pk>\d+)/update/$',
        ManageGroupView.as_view(), name='url_group_update'),

    url(r'^(?P<group_name>[\w-]+)/products/$',
        ProductList.as_view(), name='url_product_list'),
    url(r'^(?P<group_name>[\w-]+)/products/create/$',
        ProductCreate.as_view(), name='url_product_create'),
    url(r'^(?P<group_name>[\w-]+)/products/product_bases/create/$',
        ProductCreate.as_view(), name='url_productbase_create',
        kwargs={'product_class': ProductBase}),
    url(r'^(?P<group_name>[\w-]+)/products/product_bases/product_units/create/$',
        ProductCreate.as_view(), name='url_productunit_create',
        kwargs={'product_class': ProductUnit}),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/$',
        ProductRetrieve.as_view(), name='url_product_retrieve'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/update/$',
        ProductUpdate.as_view(), name='url_product_update'),
    url(r'^(?P<group_name>[\w-]+)/products/(?P<pk>\d+)/deactivate/$',
        ProductDeactivate.as_view(), name='url_product_deactivate'),

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

    url(r'^(?P<group_name>[\w-]+)/modules/self_sale/categories/$',
        ShopModuleCategories.as_view(),
        name='url_module_selfsale_categories',
        kwargs={'module_class': SelfSaleModule}),
    url(r'^(?P<group_name>[\w-]+)/modules/operator_sale/categories/$',
        ShopModuleCategories.as_view(),
        name='url_module_operatorsale_categories',
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

    url(r'^(?P<group_name>[\w-]+)/shops/$',
        ShopList.as_view(),
        name='url_shop_list'),

    url(r'^(?P<group_name>[\w-]+)/shops/create/$',
        ShopCreate.as_view(),
        name='url_shop_create'),

    url(r'^ajax/username_from_username_part/$',
        username_from_username_part,
        name='url_ajax_username_from_username_part'),

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



    url(r'^supply/lydia/self/$', SupplyLydiaSelfView.as_view(), name='url_supply_lydia_self'),
    url(r'^supply/lydia/self/confirm$', SupplyLydiaSelfConfirmView.as_view(), name='url_supply_lydia_self_confirm'),
    url(r'^supply/lydia/self/callback$', supply_lydia_self_callback, name='url_supply_lydia_self_callback'),

    url(r'^admin/', admin.site.urls),
    url(r'^local/jsi18n$', jsi18n_catalog),
    url(r'notifications/', include('notifications.urls')),

    url(r'^$', login, {'template_name': 'login.html'}, name='url_login'),  # A rediriger vers /auth/login
    url(r'^auth/login', login, {'template_name': 'login.html'}, name='url_login'),
    url(r'^auth/logout', logout, {'template_name': 'logout.html', 'next_page': login}, name='url_logout'),

    url(r'^auth/password_reset/$', password_reset, name='reset_password_reset1'),
    url(r'^auth/password_reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^auth/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^auth/done/$', password_reset_complete, name='password_reset_complete'),

    url(r'^auth/password_change$', password_change, {'post_change_redirect': password_change_done}, name='password_change'),
    url(r'^auth/password_change_done$', password_change_done),

    # Test Bootstrap CSS & components
    url('^tests/bootstrap$', TestBootstrapSober.as_view()),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Cette ligne permet d'utiliser le dossier MEDIA en
# dev (en prod c'est automatique)
