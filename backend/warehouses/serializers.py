from rest_framework import serializers
from .models import Warehouse, Location, Sku, Inventory, OutboundOrder, OutboundOrderItem

class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sku
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Location
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    sku_details = SkuSerializer(source='sku', read_only=True)
    location_details = LocationSerializer(source='bin', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'

class OutboundOrderItemSerializer(serializers.ModelSerializer):
    sku_part_number = serializers.CharField(source='sku.part_number', read_only=True)

    class Meta:
        model = OutboundOrderItem
        fields = '__all__'

class OutboundOrderSerializer(serializers.ModelSerializer):
    items = OutboundOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = OutboundOrder
        fields = '__all__'