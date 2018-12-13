from django.urls import include, path

from modules.models import OperatorSaleModule, SelfSaleModule
from modules.views import (OperatorSaleShopModuleInterface,
                           SelfSaleShopModuleInterface,
                           ShopModuleCategoryCreate, ShopModuleCategoryDelete,
                           ShopModuleCategoryUpdate, ShopModuleConfigUpdate,
                           ShopModuleConfigView)

modules_patterns = [
    path('shops/<int:shop_pk>/modules/', include([
        # SELF SALE
        path('<str:module_class>/', include([
            path('', SelfSaleShopModuleInterface.as_view(),
                 name='url_module_selfsale'),
            path('config/', ShopModuleConfigView.as_view(),
                 name='url_module_selfsale_config'),
            path('config/update/', ShopModuleConfigUpdate.as_view(), name='url_module_selfsale_config_update'),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreate.as_view(), name='url_module_selfsale_categories_create'),
                path('<int:pk>/update/', ShopModuleCategoryUpdate.as_view(), name='url_module_selfsale_categories_update'),
                path('<int:pk>/delete/', ShopModuleCategoryDelete.as_view(), name='url_module_selfsale_categories_delete')
            ]))
        ])),
        # OPERATOR SALE
        path('<str:module_class>/', include([
            path('', OperatorSaleShopModuleInterface.as_view(
            ), name='url_module_operatorsale'),
            path('config/', ShopModuleConfigView.as_view(),
                 name='url_module_operatorsale_config'),
            path('config/update', ShopModuleConfigUpdate.as_view(), name='url_module_operatorsale_config_update'),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreate.as_view(), name='url_module_operatorsale_categories_create'),
                path('<int:pk>/update/', ShopModuleCategoryUpdate.as_view(), name='url_module_operatorsale_categories_update'),
                path('<int:pk>/delete/', ShopModuleCategoryDelete.as_view(), name='url_module_operatorsale_categories_delete')
            ]))
        ]))
    ]))
]
