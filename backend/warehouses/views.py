from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OutboundOrder, Inventory
from .serializers import OutboundOrderSerializer, InventorySerializer
from .services import InventoryService, OrderService

class InventoryReceiveView(APIView):
    def post(self, request):
        """
        Endpoint for manual stock receipt.
        """
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
        """
        Endpoint to trigger the shipping process.
        """
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