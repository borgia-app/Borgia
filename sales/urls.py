#-*- coding: utf-8 -*-
from django.urls import include, path

from sales.views import SaleList, SaleRetrieve


sales_patterns = [
        path('shops/<int:shop_pk>/sales/', include([
            path('', SaleList.as_view(), name='url_sale_list'),
            path('<int:pk>/', SaleRetrieve.as_view(), name='url_sale_retrieve')
        ]))
]
