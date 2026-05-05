from django.urls import path
from .views import (
    ClientListView, ClientDetailView, SkuListView, SkuDetailView, UserListView, CountryListView, RegionListView, WarehouseDetailView,
    WarehouseListView, LocationListView, LocationDetailView,
    InventoryReceiveView, OrderFulfillmentView, OrderRevertPendingView, OrderShipView, InventoryListView,
    OrderListView, TransactionListView, ReceiptListView, ReceiptStatusUpdateView, get_region_choices, 
    BulkImportLocationView, OrderCancelView
)

urlpatterns = [
    # Dictionary Routes
    path('client/', ClientListView.as_view(), name='client-list'),
    path('client/<uuid:pk>/', ClientDetailView.as_view(), name='client-detail'),
    
    path('users/', UserListView.as_view(), name='user-list'),
    path('countries/', CountryListView.as_view(), name='country-list'),
    
    # 保持原有的 regions (复数)，以防其他旧组件还在使用
    path('regions/', RegionListView.as_view(), name='region-list'),
    
    # [核心修复 1] 匹配 WarehouseTab.vue 的单数请求路径，并去掉 api/ 前缀
    path('region/', get_region_choices, name='region-choices'),
    
    path('warehouse/', WarehouseListView.as_view(), name='warehouse-list'),
    path('warehouse/<str:pk>/', WarehouseDetailView.as_view(), name='warehouse-detail'),
    
    path('sku/list/', SkuListView.as_view(), name='sku-list'),
    path('sku/<str:pk>/', SkuDetailView.as_view(), name='sku-detail'),
    
    path('location/list/', LocationListView.as_view(), name='location-list'),
    path('location/<str:pk>/', LocationDetailView.as_view(), name='location-detail'),

    # [核心修复 2] 匹配批量导入的路径，去掉多余的 api/warehouses/ 前缀
    path('location/bulk_import/', BulkImportLocationView.as_view(), name='location-bulk-import'),

    # Inventory routes
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('inventory/receive/', InventoryReceiveView.as_view(), name='inventory-receive'),
    
    # Order routes
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<str:pk>/fulfill/', OrderFulfillmentView.as_view(), name='order-fulfill'),
    path('orders/<str:pk>/ship/', OrderShipView.as_view(), name='order-ship'),
    path('orders/<str:pk>/revert-pending/', OrderRevertPendingView.as_view(), name='order-revert-pending'),
    path('orders/<uuid:pk>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    
    # Audit & Receipt routes
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('receipts/', ReceiptListView.as_view(), name='receipt-list'),
    path('receipts/<str:pk>/status/', ReceiptStatusUpdateView.as_view(), name='receipt-status-update'),
]