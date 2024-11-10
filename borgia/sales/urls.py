from django.urls import include, path

from sales.views import SaleList, SaleRetrieve, Saledownload_xlsx


sales_patterns = [
    path('shops/<int:shop_pk>/sales/', include([
        path('', SaleList.as_view(), name='url_sale_list'),
        path('<int:sale_pk>/', SaleRetrieve.as_view(),
             name='url_sale_retrieve'),
        path('xlsx/download/', Saledownload_xlsx.as_view(),
             name='url_sales_download_xlsx')
    ]))
]
