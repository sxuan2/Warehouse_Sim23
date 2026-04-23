from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Client, Country, CountryTimezone, Region, Warehouse, Sku, Location, OutboundOrder, Inventory, InventoryTransaction, Receipt
from .serializers import (
    ClientSerializer, WarehouseSerializer, SkuSerializer, LocationSerializer,
    OutboundOrderSerializer, InventorySerializer, InventoryTransactionSerializer, ReceiptSerializer
)
from .services import InventoryService, OrderService, ReceiptService

class ClientListView(APIView):
    def get(self, request):
        clients = Client.objects.all().order_by('name')
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all().order_by('username')
        data = [
            {
                'id': u.id,
                'username': u.username,
                'display_name': (u.get_full_name() or u.username)
            }
            for u in users
        ]
        return Response(data)

class CountryListView(APIView):
    def get(self, request):
        countries = Country.objects.all().order_by('name')
        data = [{'code': c.code, 'name': c.name} for c in countries]
        return Response(data)

class RegionListView(APIView):
    def get(self, request):
        country_code = request.query_params.get('country')
        regions = Region.objects.all().order_by('name')
        if country_code:
            regions = regions.filter(country_id=country_code)
        data = [{'code': r.code, 'name': r.name, 'country': r.country_id} for r in regions]
        return Response(data)

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


class OrderRevertPendingView(APIView):
    def post(self, request, pk):
        try:
            order = OrderService.revert_to_pending(pk)
            serializer = OutboundOrderSerializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderShipView(APIView):
    def post(self, request, pk):
        try:
            order = OrderService.ship_order(pk)
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


class ReceiptStatusUpdateView(APIView):
    def post(self, request, pk):
        try:
            target_status = request.data.get('status')
            receipt = ReceiptService.update_status(pk, target_status)
            serializer = ReceiptSerializer(receipt)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
def get_region_choices(request):
    country_id = request.GET.get('country')
    if not country_id:
        return JsonResponse({'regions': [], 'timezones': []}, safe=False)
    
    # 查州
    regions = Region.objects.filter(country_id=country_id).values('code', 'name')
    # 查时区
    timezones = CountryTimezone.objects.filter(country_id=country_id).values('timezone_id', 'display_name')
    
    data = {
        'regions': [{'v': r['code'], 'n': r['name']} for r in regions],
        'timezones': [{'v': t['timezone_id'], 'n': t['display_name']} for t in timezones]
    }
    return JsonResponse(data, safe=False)