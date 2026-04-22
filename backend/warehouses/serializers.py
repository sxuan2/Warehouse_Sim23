from rest_framework import serializers
from django.db import transaction
from .models import (
    Client, Warehouse, Location, Sku, Inventory, 
    OutboundOrder, OutboundOrderItem, InventoryTransaction,
    Receipt, ReceiptItem
)

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sku
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Location
        fields = '__all__'

# (保持文件上方其他 Serializer 不变)

class InventorySerializer(serializers.ModelSerializer):
    sku_details = SkuSerializer(source='sku', read_only=True)
    location_details = LocationSerializer(source='bin', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = Inventory
        fields = [
            'id', 'sku', 'sku_details', 'bin', 'location_details', 
            'client', 'client_name', 'qty', 'serial_number', 'lot_number', 'expiry_date'
        ]

# --- Outbound Order Serializers ---
class OutboundOrderItemSerializer(serializers.ModelSerializer):
    sku_part_number = serializers.CharField(source='sku.part_number', read_only=True)
    sku_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OutboundOrderItem
        fields = '__all__'
        read_only_fields = ('order', 'sku')

class OutboundOrderSerializer(serializers.ModelSerializer):
    items = OutboundOrderItemSerializer(many=True)
    client_id = serializers.UUIDField(write_only=True)
    warehouse_id = serializers.UUIDField(write_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = OutboundOrder
        fields = '__all__'
        read_only_fields = ('client', 'warehouse')

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        client_id = validated_data.pop('client_id')
        warehouse_id = validated_data.pop('warehouse_id')
        
        client = Client.objects.get(id=client_id)
        warehouse = Warehouse.objects.get(id=warehouse_id)
        
        validated_data['client'] = client
        validated_data['warehouse'] = warehouse

        order = OutboundOrder.objects.create(**validated_data)

        for item_data in items_data:
            sku_id = item_data.pop('sku_id')
            sku = Sku.objects.get(id=sku_id)
            
            # 物理安全性校验
            if sku.client != client:
                raise serializers.ValidationError(f"SKU {sku.part_number} does not belong to {client.name}")
                
            OutboundOrderItem.objects.create(order=order, sku=sku, **item_data)
        
        return order

class InventoryTransactionSerializer(serializers.ModelSerializer):
    sku_part_number = serializers.CharField(source='sku.part_number', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    from_bin_name = serializers.CharField(source='from_bin.name', read_only=True)
    to_bin_name = serializers.CharField(source='to_bin.name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = '__all__'

# --- Receipt Serializers ---
class ReceiptItemSerializer(serializers.ModelSerializer):
    sku_part_number = serializers.CharField(source='sku.part_number', read_only=True)
    putaway_location_name = serializers.CharField(source='putaway_location.name', read_only=True)
    
    sku_id = serializers.UUIDField(write_only=True)
    putaway_location_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ReceiptItem
        fields = '__all__'
        # [FIX] 告诉 DRF 绕过自动必填校验
        read_only_fields = ('receipt', 'sku', 'putaway_location')

# (保持文件上方 imports 不变)

class ReceiptSerializer(serializers.ModelSerializer):
    items = ReceiptItemSerializer(many=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    client_id = serializers.UUIDField(write_only=True)
    warehouse_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ('client', 'warehouse')

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        client_id = validated_data.pop('client_id')
        warehouse_id = validated_data.pop('warehouse_id')
        
        validated_data['client'] = Client.objects.get(id=client_id)
        validated_data['warehouse'] = Warehouse.objects.get(id=warehouse_id)

        receipt = Receipt.objects.create(**validated_data)

        for item_data in items_data:
            sku_id = item_data.pop('sku_id')
            # [FIX] 如果前端传了空 ID，我们将其视为 None (即暂不设置上架库位)
            loc_id = item_data.pop('putaway_location_id', None)
            
            item_data['sku'] = Sku.objects.get(id=sku_id)
            if loc_id: # 只有当 ID 真实存在时才查询对象
                item_data['putaway_location'] = Location.objects.get(id=loc_id)
            
            ReceiptItem.objects.create(receipt=receipt, **item_data)
        
        return receipt