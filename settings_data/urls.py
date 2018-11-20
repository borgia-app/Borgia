from django.urls import include, path

from settings_data.views import (BalanceConfig, CenterConfig, GlobalConfig,
                                 LydiaConfig, PriceConfig)


settings_patterns = [
    path('<str:group_name>/settings/', include([
        path('', GlobalConfig.as_view(), name='url_global_config'),
        path('center/', CenterConfig.as_view(), name='url_center_config'),
        path('price/', PriceConfig.as_view(), name='url_price_config'),
        path('lydia/', LydiaConfig.as_view(), name='url_lydia_config'),
        path('balance/', BalanceConfig.as_view(), name='url_balance_config')
    ]))
]
