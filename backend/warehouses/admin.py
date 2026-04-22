from django.contrib import admin
from .models import (
    Client, Warehouse, Location, Sku, Inventory, 
    InventoryTransaction, OutboundOrder, OutboundOrderItem, OrderCharge
)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'status', 'created_at')
    list_filter = ('status', 'country')
    search_fields = ('name', 'code')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'warehouse', 'zone')
    list_filter = ('type', 'warehouse')
    search_fields = ('name',)

@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'client', 'track_by')
    list_filter = ('client',)
    search_fields = ('part_number', 'description')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('sku', 'bin', 'client', 'qty', 'serial_number', 'lot_number')
    list_filter = ('client', 'bin__warehouse')
    search_fields = ('sku__part_number', 'serial_number', 'lot_number')
    # Prevent direct modification of inventory quantity in the admin 
    # (Updates must be performed via Inventory Transactions)
    readonly_fields = ('qty',)

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'type', 'sku', 'change_qty', 'from_bin', 'to_bin', 'reference_id')
    list_filter = ('type', 'client')
    search_fields = ('sku__part_number', 'reference_id', 'serial_number')
    readonly_fields = ('timestamp', 'type', 'sku', 'client', 'change_qty', 'from_bin', 'to_bin', 'reference_id')

class OutboundOrderItemInline(admin.TabularInline):
    model = OutboundOrderItem
    extra = 0

class OrderChargeInline(admin.TabularInline):
    model = OrderCharge
    extra = 0

@admin.register(OutboundOrder)
class OutboundOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'client', 'status', 'customer_name', 'earliest_ship_date', 'created_at')
    list_filter = ('status', 'client', 'warehouse_name')
    search_fields = ('order_number', 'customer_name', 'tracking_number', 'purchase_order')
    inlines = [OutboundOrderItemInline, OrderChargeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('order_number', 'client', 'status', 'customer_name', 'warehouse_name', 'transaction_id')
        }),
        ('Dates and Purchase Orders', {
            'fields': ('purchase_order', 'earliest_ship_date', 'ship_cancel_date')
        }),
        ('Recipient Details', {
            'fields': ('contact_code', 'recipient_name', 'phone', 'email', 'address1', 'address2', 'city', 'state', 'country', 'postal_code')
        }),
        ('Shipping and Logistics', {
            'fields': ('carrier', 'tracking_number', 'service', 'billing_type', 'load_number', 'pickup_date')
        }),
        ('Special Services / Requirements', {
            'fields': ('require_return_receipt', 'saturday_delivery', 'residential_delivery', 'insurance')
        }),
    )