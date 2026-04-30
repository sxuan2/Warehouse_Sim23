from django.urls import path
from .views import (
    ClientListView, UserListView, CountryListView, RegionListView,
    WarehouseListView, SkuDictView, LocationDictView,
    InventoryReceiveView, OrderFulfillmentView, OrderRevertPendingView, OrderShipView, InventoryListView,
    OrderListView, TransactionListView, ReceiptListView, ReceiptStatusUpdateView, get_region_choices, BulkImportLocationView
)

urlpatterns = [
    # Dictionary Routes
    path('client/', ClientListView.as_view(), name='client-list'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('regions/', RegionListView.as_view(), name='region-list'),
    path('warehouse/', WarehouseListView.as_view(), name='warehouse-list'),
    path('sku/', SkuDictView.as_view(), name='sku-dict'),
    path('location/', LocationDictView.as_view(), name='location-dict'),

    # Inventory routes
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('inventory/receive/', InventoryReceiveView.as_view(), name='inventory-receive'),
    
    # Order routes
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<str:pk>/fulfill/', OrderFulfillmentView.as_view(), name='order-fulfill'),
    path('orders/<str:pk>/ship/', OrderShipView.as_view(), name='order-ship'),
    path('orders/<str:pk>/revert-pending/', OrderRevertPendingView.as_view(), name='order-revert-pending'),
    
    # Audit & Receipt routes
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('receipts/', ReceiptListView.as_view(), name='receipt-list'),
    path('receipts/<str:pk>/status/', ReceiptStatusUpdateView.as_view(), name='receipt-status-update'),
    
    path('api/regions/', get_region_choices, name='api_regions'),
    path('api/warehouses/location/bulk_import/', BulkImportLocationView.as_view(), name='location-bulk-import'),
]