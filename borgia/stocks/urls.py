from django.urls import include, path

from stocks.views import (InventoryListView, InventoryRetrieveView,
                          InventoryCreateView, StockEntryCreateView,
                          StockEntryListView, StockEntryRetrieveView)


stocks_patterns = [
    path('shops/<int:shop_pk>/stocks/', include([
        path('entries/', include([
            path('', StockEntryListView.as_view(), name='url_stockentry_list'),
            path('create/', StockEntryCreateView.as_view(), name='url_stockentry_create'),
            path('<int:stockentry_pk>/', StockEntryRetrieveView.as_view(), name='url_stockentry_retrieve'),
        ])),
        path('inventories/', include([
            path('', InventoryListView.as_view(), name='url_inventory_list'),
            path('create/', InventoryCreateView.as_view(), name='url_inventory_create'),
            path('<int:inventory_pk>/', InventoryRetrieveView.as_view(), name='url_inventory_retrieve'),
        ]))
    ]))
]
