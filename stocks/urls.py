from django.urls import include, path

from stocks.views import (InventoryList, InventoryRetrieve,
                          ShopInventoryCreate, ShopStockEntryCreate,
                          StockEntryList, StockEntryRetrieve)


stocks_patterns = [
    path('<str:group_name>/stocks/', include([
        path('entries/', include([
            path('', StockEntryList.as_view(), name='url_stock_entry_list'),
            path('create/', ShopStockEntryCreate.as_view(), name='url_stock_entry_create'),
            path('<int:pk>/', StockEntryRetrieve.as_view(), name='url_stock_entry_retrieve'),
        ])),
        path('inventories/', include([
            path('', InventoryList.as_view(), name='url_inventory_list'),
            path('create/', ShopInventoryCreate.as_view(), name='url_inventory_create'),
            path('<int:pk>/', InventoryRetrieve.as_view(), name='url_inventory_retrieve'),
        ]))
    ]))
]
