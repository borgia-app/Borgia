from django.urls import include, path

from modules.models import OperatorSaleModule, SelfSaleModule
from modules.views import (OperatorSaleShopModuleInterface,
                           OperatorSaleShopModuleConfig,
                           SelfSaleShopModuleInterface,
                           SelfSaleShopModuleConfig,
                           ShopModuleCategoryCreate, ShopModuleCategoryDelete,
                           ShopModuleCategoryUpdate, ShopModuleConfigUpdate)

modules_patterns = [
    path('shops/<int:shop_pk>/modules/', include([
        # SELF SALE
        path('self_sales/', include([
            path('', SelfSaleShopModuleInterface.as_view(), name='url_module_selfsale'),
            path('config/', SelfSaleShopModuleConfig.as_view(), name='url_module_selfsale_config'),
            path('config/update/', ShopModuleConfigUpdate.as_view(), name='url_module_selfsale_config_update',
                 kwargs={'module_class': SelfSaleModule}),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreate.as_view(), name='url_module_selfsale_categories_create',
                     kwargs={'module_class': SelfSaleModule}),
                path('<int:pk>/update/', ShopModuleCategoryUpdate.as_view(), name='url_module_selfsale_categories_update',
                     kwargs={'module_class': SelfSaleModule}),
                path('<int:pk>/delete/', ShopModuleCategoryDelete.as_view(), name='url_module_selfsale_categories_delete',
                     kwargs={'module_class': SelfSaleModule})
            ]))
        ])),
        # OPERATOR SALE
        path('operator_sales/', include([
            path('', OperatorSaleShopModuleInterface.as_view(
            ), name='url_module_operatorsale'),
            path('config/', OperatorSaleShopModuleConfig.as_view(),
                 name='url_module_operatorsale_config'),
            path('config/update', ShopModuleConfigUpdate.as_view(), name='url_module_operatorsale_config_update',
                 kwargs={'module_class': OperatorSaleModule}),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreate.as_view(), name='url_module_operatorsale_categories_create',
                     kwargs={'module_class': OperatorSaleModule}),
                path('<int:pk>/update/', ShopModuleCategoryUpdate.as_view(), name='url_module_operatorsale_categories_update',
                     kwargs={'module_class': OperatorSaleModule}),
                path('<int:pk>/delete/', ShopModuleCategoryDelete.as_view(), name='url_module_operatorsale_categories_delete',
                     kwargs={'module_class': OperatorSaleModule})
            ]))
        ]))
    ]))
]
