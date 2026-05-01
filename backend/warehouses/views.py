from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Client, Country, CountryTimezone, Region, Warehouse, Sku, Location, Order, Inventory, InventoryTransaction, Receipt
from .serializers import (
    ClientSerializer, WarehouseSerializer, SkuSerializer, LocationSerializer,
    OrderSerializer, InventorySerializer, InventoryTransactionSerializer, ReceiptSerializer
)
from .services import InventoryService, OrderService, ReceiptService

#######################################################################

# 找到原来的 ClientListView，替换并增加以下代码
class ClientListView(APIView):
    def get(self, request):
        clients = Client.objects.all().order_by('name')
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientDetailView(APIView):
    def get_object(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return None

    # 修改客户
    def put(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = ClientSerializer(client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 删除客户
    def delete(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            client.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # 拦截数据库外键保护错误 (例如该客户已经有订单了，不能删)
            return Response(
                {"error": "Cannot delete this customer. They may have linked inventory or orders."}, 
                status=status.HTTP_409_CONFLICT
            )

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

    # 处理新建仓库的 POST 请求
    def post(self, request):
        serializer = WarehouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 处理特定仓库的修改和删除
class WarehouseDetailView(APIView):
    def get_object(self, pk):
        try:
            return Warehouse.objects.get(pk=pk)
        except Warehouse.DoesNotExist:
            return None

    # 修改仓库
    def put(self, request, pk):
        warehouse = self.get_object(pk)
        if not warehouse:
            return Response({"error": "Warehouse not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = WarehouseSerializer(warehouse, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 删除仓库
    def delete(self, request, pk):
        warehouse = self.get_object(pk)
        if not warehouse:
            return Response({"error": "Warehouse not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            warehouse.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # 拦截数据库外键保护错误 (例如该仓库下已有库位 Location)
            return Response(
                {"error": "Cannot delete this warehouse. It contains locations or inventory."}, 
                status=status.HTTP_409_CONFLICT
            )

class SkuListView(APIView):
    def get(self, request):
        # 默认按客户和零件号排序
        skus = Sku.objects.all().order_by('client__name', 'part_number')
        serializer = SkuSerializer(skus, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SkuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SkuDetailView(APIView):
    def get_object(self, pk):
        try:
            return Sku.objects.get(pk=pk)
        except Sku.DoesNotExist:
            return None

    def put(self, request, pk):
        sku = self.get_object(pk)
        if not sku:
            return Response({"error": "SKU not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = SkuSerializer(sku, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        sku = self.get_object(pk)
        if not sku:
            return Response({"error": "SKU not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            sku.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": "Cannot delete this SKU. It may have linked inventory or order histories."}, 
                status=status.HTTP_409_CONFLICT
            )
                
class LocationListView(APIView):
    def get(self, request):
        # 默认按库区和拣货路径排序
        locations = Location.objects.all().order_by('zone', 'pick_path', 'name')
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LocationDetailView(APIView):
    def get_object(self, pk):
        try:
            return Location.objects.get(pk=pk)
        except Location.DoesNotExist:
            return None

    def put(self, request, pk):
        location = self.get_object(pk)
        if not location:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = LocationSerializer(location, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        location = self.get_object(pk)
        if not location:
            return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            location.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": "Cannot delete this location. It may contain active inventory."}, 
                status=status.HTTP_409_CONFLICT
            )
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
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderRevertPendingView(APIView):
    def post(self, request, pk):
        try:
            order = OrderService.revert_to_pending(pk)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class OrderShipView(APIView):
    def post(self, request, pk):
        try:
            order = OrderService.ship_order(pk)
            serializer = OrderSerializer(order)
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
        orders = Order.objects.prefetch_related('items__sku').all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
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

class BulkImportLocationView(APIView):
    """
    API view for handling bulk import of locations via JSON payload.
    Ensures strict database integrity using atomic transactions.
    """
    def post(self, request):
        data = request.data
        
        # Validate that the incoming payload is a list/array
        if not isinstance(data, list):
            return Response({
                "error": "Invalid data format: Expected a list of JSON objects."
            }, status=status.HTTP_400_BAD_REQUEST)

        locations_to_create = []
        
        try:
            # Open a strict atomic transaction: rollback everything if ANY error occurs
            with transaction.atomic():
                for index, row in enumerate(data):
                    # 1. Validate Foreign Key: Warehouse
                    warehouse_obj = None
                    if row.get('warehouse_id'):
                        try:
                            warehouse_obj = Warehouse.objects.get(id=row['warehouse_id'])
                        except Warehouse.DoesNotExist:
                            # This will trigger the ValueError exception block and rollback
                            raise ValueError(f"Row {index + 1} Error: Warehouse ID {row['warehouse_id']} does not exist.")

                    # 2. Construct Location object mapping from the JSON row
                    loc = Location(
                        name=row['name'],
                        warehouse=warehouse_obj,
                        type=row.get('type', 'STORAGE'),
                        zone=row.get('zone', ''),
                        description=row.get('description', ''),
                        pick_path=int(row.get('pick_path') or 0),
                        is_non_pickable=bool(row.get('is_non_pickable', False)),
                        width=float(row.get('width') or 0),
                        length=float(row.get('length') or 0),
                        height=float(row.get('height') or 0),
                        max_weight=float(row.get('max_weight') or 0),
                        min_temperature=float(row.get('min_temperature') or 0),
                        min_quantity=int(row.get('min_quantity') or 0),
                        allocation_priority=int(row.get('allocation_priority') or 10),
                        billing_type=row.get('billing_type', '')
                    )
                    locations_to_create.append(loc)
                
                # 3. Execute bulk insert to heavily optimize database I/O
                Location.objects.bulk_create(locations_to_create)
                
            # If execution reaches here, the transaction is successfully committed
            return Response({
                "success": True, 
                "message": f"Successfully imported {len(locations_to_create)} locations.",
                "count": len(locations_to_create)
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # Catch unique constraint violations (e.g., duplicate Location ID) and rollback
            return Response({
                "error": f"Database Conflict (Rolled back): {str(e)}"
            }, status=status.HTTP_409_CONFLICT)
            
        except ValueError as e:
            # Catch custom validation errors (e.g., Warehouse missing) and rollback
            return Response({
                "error": f"Validation Failed (Rolled back): {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Catch any other unexpected system exceptions and rollback
            return Response({
                "error": f"System Error (Rolled back): {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)