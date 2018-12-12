from django.urls import include, path

from configurations.views import (ConfigurationBalanceView,
                                  ConfigurationCenterView,
                                  ConfigurationListView,
                                  ConfigurationLydiaView,
                                  ConfigurationProfitView)

configurations_patterns = [
    path('<str:group_name>/configurations/', include([
        path('', ConfigurationListView.as_view(), name='url_global_config'),
        path('center/', ConfigurationCenterView.as_view(),
             name='url_center_config'),
        path('price/', ConfigurationProfitView.as_view(), name='url_price_config'),
        path('lydia/', ConfigurationLydiaView.as_view(), name='url_lydia_config'),
        path('balance/', ConfigurationBalanceView.as_view(),
             name='url_balance_config')
    ]))
]
