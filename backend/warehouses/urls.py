from django.urls import path
from .views import InventoryReceiveView, OrderFulfillmentView, InventoryListView

urlpatterns = [
    path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('inventory/receive/', InventoryReceiveView.as_view(), name='inventory-receive'),
    path('orders/<uuid:pk>/fulfill/', OrderFulfillmentView.as_view(), name='order-fulfill'),
]