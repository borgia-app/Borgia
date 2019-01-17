from django.urls import include, path

from modules.views import (ShopModuleSaleView,
                           ShopModuleCategoryCreateView, ShopModuleCategoryDeleteView,
                           ShopModuleCategoryUpdateView, ShopModuleConfigUpdateView,
                           ShopModuleConfigView)

modules_patterns = [
    path('shops/<int:shop_pk>/modules/', include([
        path('<str:module_class>/', include([
            path('', ShopModuleSaleView.as_view(), name='url_shop_module_sale'),
            path('config/', ShopModuleConfigView.as_view(),
                 name='url_shop_module_config'),
            path('config/update/', ShopModuleConfigUpdateView.as_view(),
                 name='url_shop_module_config_update'),
            path('categories/', include([
                path('create/', ShopModuleCategoryCreateView.as_view(),
                     name='url_shop_module_category_create'),
                path('<int:category_pk>/', include([
                    path('update/', ShopModuleCategoryUpdateView.as_view(),
                         name='url_shop_module_category_update'),
                    path('delete/', ShopModuleCategoryDeleteView.as_view(),
                         name='url_shop_module_category_delete')
                ]))
            ]))
        ]))
    ]))
]
