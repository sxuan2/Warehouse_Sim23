from django.urls import path
from .views import (
    ClientListView, WarehouseListView, SkuDictView, LocationDictView,
    InventoryReceiveView, OrderFulfillmentView, InventoryListView, 
    OrderListView, TransactionListView, ReceiptListView
)

urlpatterns = [
    # Dictionary Routes
    path('client/', ClientListView.as_view(), name='client-list'),
    path('warehouse/', WarehouseListView.as_view(), name='warehouse-list'),
    path('sku/', SkuDictView.as_view(), name='sku-dict'),
    path('location/', LocationDictView.as_view(), name='location-dict'),

    # Inventory routes
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('inventory/receive/', InventoryReceiveView.as_view(), name='inventory-receive'),
    
    # Order routes
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:pk>/fulfill/', OrderFulfillmentView.as_view(), name='order-fulfill'),
    
    # Audit & Receipt routes
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('receipts/', ReceiptListView.as_view(), name='receipt-list'),
]