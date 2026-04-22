from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from .models import (
    Client, Warehouse, Location, Sku, Inventory, 
    InventoryTransaction, OutboundOrder, OutboundOrderItem,
    Receipt, ReceiptItem
)

# -----------------------------------------------------------------------------------------
# 1. CLIENT ADMIN (支持仓库多对多权限分配)
# -----------------------------------------------------------------------------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'alias_id', 'status', 'contact_name', 'phone', 'city', 'country', 'created_at')
    search_fields = ('name', 'alias_id', 'contact_name', 'email')
    list_filter = ('status', 'country', 'state')
    filter_horizontal = ('warehouses',) 
    
    fieldsets = (
        ('Customer Information', {
            'fields': (
                ('name', 'alias_id', 'status'),
                ('phone', 'fax'),
                ('website', 'email')
            )
        }),
        ('Address', {
            'fields': (
                'country', 
                ('address1', 'address2'), 
                ('state', 'city', 'postal_code')
            )
        }),
        ('Primary Contact', {
            'fields': (
                ('contact_name', 'contact_phone', 'contact_email'),
            )
        }),
        ('Warehouse Access', {
            'fields': ('warehouses',)
        }),
    )

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'status', 'created_at')
    list_filter = ('status', 'country')
    search_fields = ('name', 'code')

# -----------------------------------------------------------------------------------------
# 2. LOCATION ADMIN (还原 Extensiv 库位页签布局)
# -----------------------------------------------------------------------------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse', 'zone', 'type', 'description', 'is_non_pickable')
    list_filter = ('type', 'warehouse', 'is_non_pickable')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('name', 'type', 'description'),
                ('warehouse', 'zone', 'pick_path'),
                'is_non_pickable'
            )
        }),
        ('Capabilities', {
            'fields': (
                ('width', 'length', 'height'),
                ('max_weight', 'min_temperature', 'min_quantity')
            )
        }),
        ('Priorities', {
            'fields': ('allocation_priority',)
        }),
        ('Billing', {
            'fields': ('billing_type',)
        })
    )

# -----------------------------------------------------------------------------------------
# 3. SKU & INVENTORY ADMIN
# -----------------------------------------------------------------------------------------
@admin.register(Sku)
class SkuAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'client', 'track_by', 'created_at')
    list_filter = ('client',)
    search_fields = ('part_number', 'description')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('sku', 'bin', 'client', 'qty', 'serial_number', 'lot_number')
    list_filter = ('client', 'bin__warehouse')
    search_fields = ('sku__part_number', 'serial_number', 'lot_number')
    readonly_fields = ('qty',)

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'type', 'sku', 'change_qty', 'from_bin', 'to_bin', 'reference_id')
    list_filter = ('type', 'client')
    search_fields = ('sku__part_number', 'reference_id', 'serial_number')
    readonly_fields = ('timestamp', 'type', 'sku', 'client', 'change_qty', 'from_bin', 'to_bin', 'reference_id')

# -----------------------------------------------------------------------------------------
# 4. OUTBOUND ORDER ADMIN (极致还原，包含所有承运、路由、小包裹字段)
# -----------------------------------------------------------------------------------------
class OutboundOrderItemInline(admin.TabularInline):
    model = OutboundOrderItem
    extra = 0
    fields = ('sku', 'qty', 'uom', 'price', 'weight', 'volume')

@admin.register(OutboundOrder)
class OutboundOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'client', 'warehouse', 'transaction_id', 'purchase_order', 'status', 'created_by', 'earliest_ship_date', 'created_at')
    list_filter = ('status', 'client', 'warehouse')
    search_fields = ('order_number', 'recipient_name', 'company_name', 'transaction_id', 'tracking_number')
    inlines = [OutboundOrderItemInline]
    
    fieldsets = (
        ('Order Information Header', {
            'fields': (
                ('order_number', 'transaction_id', 'status'),
                ('client', 'warehouse', 'purchase_order'),
                ('earliest_ship_date', 'ship_cancel_date', 'created_by')
            )
        }),
        ('Order Contact Details (Shipping Destination)', {
            'fields': (
                ('recipient_name', 'company_name'),
                ('email', 'phone'),
                ('address1', 'address2'),
                ('country', 'state', 'city', 'postal_code'),
                ('retailer_id', 'department_number') # [FIXED] 还原原始字段名
            )
        }),
        ('Carrier and Routing Details', {
            'fields': (
                ('carrier', 'scac', 'service'),
                ('billing_type', 'account_number', 'account_zip'),
                ('tracking_number', 'load_number', 'bol_number'),
                ('trailer_number', 'seal_number', 'door'),
                ('capacity_type', 'pickup_date'),
                ('warehouse_instructions', 'carrier_instructions')
            )
        }),
        ('Small Parcel Shipping Options', {
            'fields': (
                ('require_return_receipt', 'saturday_delivery', 'residential_delivery'),
                ('insurance', 'insurance_amount')
            )
        }),
        ('Order Totals & UOM Summary', {
            'fields': (
                ('total_packages', 'packaging_uom', 'total_weight'),
                ('total_movable_units', 'mu_uom', 'total_volume')
            )
        })
    )

# -----------------------------------------------------------------------------------------
# 5. INBOUND RECEIPT ADMIN (包含托盘明细、自动入库 Action)
# -----------------------------------------------------------------------------------------
class ReceiptItemInline(admin.StackedInline):
    model = ReceiptItem
    extra = 0
    fieldsets = (
        ('Item Base Info', {
            'fields': (('sku', 'qty', 'weight_lbs'), ('lot_number', 'expiration_date'))
        }),
        ('Movable Unit (MU) Details', {
            'fields': (
                ('mu_label', 'split_mu', 'primary_units_per_mu', 'mu_type'), 
                ('length_in', 'width_in', 'height_in', 'mu_weight_lbs')
            )
        }),
        ('Putaway & Hold Status', {
            'fields': (('putaway_location', 'is_on_hold'), 'custom_fields')
        })
    )

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('status', 'transaction_id', 'reference_number', 'created_at', 'client', 'warehouse', 'purchase_order_number', 'trailer_pro_number')
    list_filter = ('status', 'client', 'warehouse')
    search_fields = ('transaction_id', 'reference_number', 'purchase_order_number', 'receipt_advice_number')
    inlines = [ReceiptItemInline]
    actions = ['mark_as_complete']
    
    fieldsets = (
        ('General Receipt Information', {
            'fields': (
                ('transaction_id', 'status', 'client', 'warehouse'), 
                ('reference_number', 'purchase_order_number', 'receipt_advice_number')
            )
        }),
        ('Logistics & Dates', {
            'fields': (
                ('arrival_date', 'expected_arrival_date'), 
                'trailer_pro_number'
            )
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        })
    )

    @admin.action(description="Mark selected receipts as COMPLETE and add to Inventory")
    def mark_as_complete(self, request, queryset):
        success_count = 0
        error_count = 0
        for receipt in queryset:
            if receipt.status != Receipt.StatusChoices.OPEN:
                error_count += 1
                continue
            try:
                with transaction.atomic():
                    for item in receipt.items.all():
                        target_bin = item.putaway_location
                        if not target_bin:
                            # 备选入库月台
                            target_bin, _ = Location.objects.get_or_create(
                                warehouse=receipt.warehouse, 
                                name=f"RECV-DOCK-{receipt.warehouse.code}",
                                defaults={'type': Location.TypeChoices.STAGING}
                            )
                        
                        # 增加库存账本
                        inv, _ = Inventory.objects.get_or_create(
                            sku=item.sku, bin=target_bin, client=receipt.client, 
                            lot_number=item.lot_number, defaults={'qty': 0}
                        )
                        inv.qty += item.qty
                        if item.expiration_date: inv.expiry_date = item.expiration_date
                        inv.save()
                        
                        # 记录流水审计
                        InventoryTransaction.objects.create(
                            type=InventoryTransaction.TypeChoices.INBOUND,
                            sku=item.sku,
                            client=receipt.client,
                            change_qty=item.qty,
                            to_bin=target_bin,
                            reference_id=f"RECV-{receipt.transaction_id}",
                            reason="Receipt Fulfillment",
                            lot_number=item.lot_number
                        )
                    
                    receipt.status = Receipt.StatusChoices.COMPLETE
                    receipt.save()
                    success_count += 1
            except Exception as e:
                self.message_user(request, f"Error on {receipt.transaction_id}: {str(e)}", level='ERROR')
        self.message_user(request, f"Successfully processed {success_count} receipts. Skipped {error_count}.")