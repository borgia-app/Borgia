from django.urls import include, path

from modules.models import OperatorSaleModule, SelfSaleModule
from modules.views import (ShopModuleSaleView,
                           ShopModuleCategoryCreateView, ShopModuleCategoryDeleteView,
                           ShopModuleCategoryUpdateView, ShopModuleConfigUpdateView,
                           ShopModuleConfigView)

modules_patterns = [
    path('shops/<int:shop_pk>/modules/', include([
        # SELF SALE
        path('<str:module_class>/', include([
            path('', ShopModuleSaleView.as_view(),
                 name='url_module_selfsale'),
            path('config/', ShopModuleConfigView.as_view(),
                 name='url_module_selfsale_config'),
            path('config/update/', ShopModuleConfigUpdateView.as_view(), name='url_module_selfsale_config_update'),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreateView.as_view(), name='url_module_selfsale_categories_create'),
                path('<int:pk>/update/', ShopModuleCategoryUpdateView.as_view(), name='url_module_selfsale_categories_update'),
                path('<int:pk>/delete/', ShopModuleCategoryDeleteView.as_view(), name='url_module_selfsale_categories_delete')
            ]))
        ])),
        # OPERATOR SALE
        path('<str:module_class>/', include([
            path('', ShopModuleSaleView.as_view(
            ), name='url_module_operatorsale'),
            path('config/', ShopModuleConfigView.as_view(),
                 name='url_module_operatorsale_config'),
            path('config/update', ShopModuleConfigUpdateView.as_view(), name='url_module_operatorsale_config_update'),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreateView.as_view(), name='url_module_operatorsale_categories_create'),
                path('<int:pk>/update/', ShopModuleCategoryUpdateView.as_view(), name='url_module_operatorsale_categories_update'),
                path('<int:pk>/delete/', ShopModuleCategoryDeleteView.as_view(), name='url_module_operatorsale_categories_delete')
            ]))
        ]))
    ]))
]
