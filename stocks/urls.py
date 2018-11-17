from django.urls import include, path

from stocks.views import (InventoryListView, InventoryRetrieveView,
                          InventoryCreateView, StockEntryCreateView,
                          StockEntryListView, StockEntryRetrieveView)


stocks_patterns = [
    path('<str:group_name>/stocks/', include([
        path('entries/', include([
            path('', StockEntryListView.as_view(), name='url_stock_entry_list'),
            path('create/', StockEntryCreateView.as_view(), name='url_stock_entry_create'),
            path('<int:pk>/', StockEntryRetrieveView.as_view(), name='url_stock_entry_retrieve'),
        ])),
        path('inventories/', include([
            path('', InventoryListView.as_view(), name='url_inventory_list'),
            path('create/', InventoryCreateView.as_view(), name='url_inventory_create'),
            path('<int:pk>/', InventoryRetrieveView.as_view(), name='url_inventory_retrieve'),
        ]))
    ]))
]
