from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Client, Warehouse, Sku, Location, OutboundOrder, Inventory, InventoryTransaction, Receipt
from .serializers import (
    ClientSerializer, WarehouseSerializer, SkuSerializer, LocationSerializer,
    OutboundOrderSerializer, InventorySerializer, InventoryTransactionSerializer, ReceiptSerializer
)
from .services import InventoryService, OrderService

class ClientListView(APIView):
    def get(self, request):
        clients = Client.objects.all().order_by('name')
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

class WarehouseListView(APIView):
    def get(self, request):
        warehouses = Warehouse.objects.all().order_by('name')
        serializer = WarehouseSerializer(warehouses, many=True)
        return Response(serializer.data)

class SkuDictView(APIView):
    def get(self, request):
        """
        Modified to support filtering by client_id.
        Usage: /api/warehouses/sku/?client_id=<uuid>
        """
        client_id = request.query_params.get('client_id')
        queryset = Sku.objects.all().order_by('part_number')
        
        if client_id:
            queryset = queryset.filter(client_id=client_id)
            
        serializer = SkuSerializer(queryset, many=True)
        return Response(serializer.data)

class LocationDictView(APIView):
    def get(self, request):
        locations = Location.objects.all().order_by('name')
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

class InventoryReceiveView(APIView):
    def post(self, request):
        try:
            sku_id = request.data.get('skuId')
            bin_id = request.data.get('binId')
            qty = int(request.data.get('qty', 0))
            client_id = request.data.get('clientId')
            
            transaction = InventoryService.receive_stock(sku_id, bin_id, qty, client_id)
            return Response({"success": True, "transaction_id": transaction.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderFulfillmentView(APIView):
    def post(self, request, pk):
        try:
            order = OrderService.fulfill_order(pk)
            serializer = OutboundOrderSerializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InventoryListView(APIView):
    def get(self, request):
        inventory = Inventory.objects.all()
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data)

class OrderListView(APIView):
    def get(self, request):
        orders = OutboundOrder.objects.prefetch_related('items__sku').all().order_by('-created_at')
        serializer = OutboundOrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OutboundOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionListView(APIView):
    def get(self, request):
        transactions = InventoryTransaction.objects.select_related(
            'sku', 'client', 'from_bin', 'to_bin'
        ).all().order_by('-timestamp')
        serializer = InventoryTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class ReceiptListView(APIView):
    def get(self, request):
        receipts = Receipt.objects.prefetch_related(
            'items__sku', 'items__putaway_location'
        ).select_related('client', 'warehouse').all().order_by('-created_at')
        serializer = ReceiptSerializer(receipts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReceiptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)