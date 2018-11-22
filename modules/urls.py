from django.urls import include, path

from modules.models import OperatorSaleModule, SelfSaleModule
from modules.views import (OperatorSaleShopModuleInterface,
                           OperatorSaleShopModuleWorkboard,
                           SelfSaleShopModuleInterface,
                           SelfSaleShopModuleWorkboard,
                           ShopModuleCategoryCreate, ShopModuleCategoryDelete,
                           ShopModuleCategoryUpdate, ShopModuleConfig)

modules_patterns = [
    path('<str:group_name>/modules/', include([
        # SELF SALE
        path('self_sales/', include([
            path('', SelfSaleShopModuleWorkboard.as_view(), name='url_module_selfsale_workboard'),
            path('config/', ShopModuleConfig.as_view(), name='url_module_selfsale_config',
                 kwargs={'module_class': SelfSaleModule}),
            path('<str:shop_name>', SelfSaleShopModuleInterface.as_view(), name='url_module_selfsale'),
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
            path('', OperatorSaleShopModuleWorkboard.as_view(), name='url_module_operatorsale_workboard'),
            path('config/', ShopModuleConfig.as_view(), name='url_module_operatorsale_config',
                 kwargs={'module_class': OperatorSaleModule}),
            path('<str:shop_name>', OperatorSaleShopModuleInterface.as_view(), name='url_module_operatorsale'),
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
