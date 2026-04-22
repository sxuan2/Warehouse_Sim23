import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Client Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'wms_client'
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.name

class Warehouse(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        INACTIVE = 'INACTIVE', _('Inactive')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Warehouse Name")
    code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Warehouse Code")
    zone = models.CharField(max_length=100, null=True, blank=True, verbose_name="Zone")
    address1 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 1")
    address2 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 2")
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Country")
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name="State/Province")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="City")
    postal_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Postal Code")
    time_zone = models.CharField(max_length=100, null=True, blank=True, verbose_name="Time Zone")
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name="Phone")
    fax = models.CharField(max_length=50, null=True, blank=True, verbose_name="Fax")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        db_table = 'wms_warehouse'
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"

    def __str__(self):
        return f"{self.name} ({self.code})"

class Location(models.Model):
    class TypeChoices(models.TextChoices):
        STORAGE = 'STORAGE', _('Storage')
        DOCK = 'DOCK', _('Dock')
        PACKING = 'PACKING', _('Packing')
        PICKING = 'PICKING', _('Picking')
        BULK = 'BULK', _('Bulk')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Location Name")
    zone = models.CharField(max_length=100, null=True, blank=True, verbose_name="Location Zone")
    type = models.CharField(max_length=50, choices=TypeChoices.choices, default=TypeChoices.PICKING, verbose_name="Location Type")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.RESTRICT, related_name='locations', null=True, blank=True, verbose_name="Warehouse")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        db_table = 'wms_location'
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"

class Sku(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='skus', verbose_name="Client")
    part_number = models.CharField(max_length=100, verbose_name="Part Number (SKU)")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    track_by = models.CharField(max_length=50, default="NONE", verbose_name="Track By")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'wms_sku'
        unique_together = ('client', 'part_number')
        verbose_name = "SKU"
        verbose_name_plural = "SKUs"

    def __str__(self):
        return self.part_number

class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.ForeignKey(Sku, on_delete=models.RESTRICT, related_name='inventory', verbose_name="SKU")
    bin = models.ForeignKey(Location, on_delete=models.RESTRICT, related_name='inventory', verbose_name="Location")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='inventory', verbose_name="Client")
    qty = models.IntegerField(default=0, verbose_name="On-hand Quantity")
    serial_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Serial Number")
    lot_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Lot Number")
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="Expiry Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        db_table = 'wms_inventory'
        # Matches Prisma's @@unique([skuId, binId, serialNumber, lotNumber])
        unique_together = ('sku', 'bin', 'serial_number', 'lot_number')
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory Details"

    def __str__(self):
        return f"{self.sku.part_number} | {self.bin.name} | Qty: {self.qty}"

class InventoryTransaction(models.Model):
    class TypeChoices(models.TextChoices):
        INBOUND = 'INBOUND', _('Inbound')
        OUTBOUND = 'OUTBOUND', _('Outbound')
        TRANSFER = 'TRANSFER', _('Transfer')
        ADJUSTMENT = 'ADJUSTMENT', _('Adjustment')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=TypeChoices.choices, verbose_name="Transaction Type")
    sku = models.ForeignKey(Sku, on_delete=models.RESTRICT, related_name='transactions', verbose_name="SKU")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='transactions', verbose_name="Client")
    change_qty = models.IntegerField(verbose_name="Change Quantity")
    from_bin = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_from', verbose_name="From Location")
    to_bin = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_to', verbose_name="To Location")
    reference_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Reference ID")
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="Reason")
    serial_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Serial Number")
    lot_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Lot Number")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")

    class Meta:
        db_table = 'wms_inventory_transaction'
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"

    def __str__(self):
        return f"{self.get_type_display()} | {self.sku.part_number} | {self.change_qty}"

class OutboundOrder(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        SHIPPED = 'SHIPPED', _('Shipped')
        CANCELLED = 'CANCELLED', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=100, unique=True, verbose_name="Order Number")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', verbose_name="Client")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name="Status")
    customer_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Customer Name (Ship-To)")
    
    # Basic Order Info
    warehouse_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ship-From Warehouse")
    transaction_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="Transaction ID")
    purchase_order = models.CharField(max_length=100, null=True, blank=True, verbose_name="Purchase Order (PO)")
    earliest_ship_date = models.DateTimeField(null=True, blank=True, verbose_name="Earliest Ship Date")
    ship_cancel_date = models.DateTimeField(null=True, blank=True, verbose_name="Ship Cancel Date")
    
    # Contact and Address
    contact_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="Contact Code")
    recipient_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Recipient Name")
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name="Phone")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    address1 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 1")
    address2 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 2")
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Country")
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name="State/Province")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="City")
    postal_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Postal Code")
    retailer_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="Retailer ID")
    department_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Department Number")
    
    # Summary Data
    total_packages = models.IntegerField(null=True, blank=True, verbose_name="Total Packages")
    packaging_uom = models.CharField(max_length=50, null=True, blank=True, verbose_name="Packaging UOM")
    total_weight = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, verbose_name="Total Weight")
    total_volume = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, verbose_name="Total Volume")
    
    # Carrier and Routing
    carrier = models.CharField(max_length=100, null=True, blank=True, verbose_name="Carrier")
    scac = models.CharField(max_length=50, null=True, blank=True, verbose_name="SCAC Code")
    service = models.CharField(max_length=100, null=True, blank=True, verbose_name="Service Type")
    billing_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Billing Type")
    account_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Account Number")
    account_zip = models.CharField(max_length=50, null=True, blank=True, verbose_name="Account Zip Code")
    tracking_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Tracking Number")
    warehouse_instructions = models.TextField(null=True, blank=True, verbose_name="Warehouse Instructions")
    carrier_instructions = models.TextField(null=True, blank=True, verbose_name="Carrier Instructions")
    load_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Load Number")
    bol_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="BOL Number")
    trailer_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Trailer Number")
    seal_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Seal Number")
    door = models.CharField(max_length=50, null=True, blank=True, verbose_name="Door")
    capacity_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Capacity Type")
    pickup_date = models.DateTimeField(null=True, blank=True, verbose_name="Pickup Date")
    
    # Shipment Requirements
    require_return_receipt = models.BooleanField(default=False, verbose_name="Require Return Receipt")
    saturday_delivery = models.BooleanField(default=False, verbose_name="Saturday Delivery")
    residential_delivery = models.BooleanField(default=False, verbose_name="Residential Delivery")
    insurance = models.BooleanField(default=False, verbose_name="Insurance")
    insurance_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Insurance Type")
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Insurance Amount")
    delivery_confirmation = models.CharField(max_length=100, null=True, blank=True, verbose_name="Delivery Confirmation")
    dry_weight = models.CharField(max_length=100, null=True, blank=True, verbose_name="Dry Weight")
    intl_contents_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="International Contents Type")
    intl_non_delivery = models.CharField(max_length=100, null=True, blank=True, verbose_name="International Non-Delivery Instructions")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'wms_outbound_order'
        verbose_name = "Outbound Order"
        verbose_name_plural = "Outbound Orders"

    def __str__(self):
        return f"{self.order_number} - {self.get_status_display()}"

class OutboundOrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(OutboundOrder, on_delete=models.CASCADE, related_name='items', verbose_name="Order")
    sku = models.ForeignKey(Sku, on_delete=models.RESTRICT, related_name='outbound_order_items', verbose_name="SKU")
    qty = models.IntegerField(verbose_name="Quantity Ordered")
    picked_qty = models.IntegerField(default=0, verbose_name="Quantity Picked")
    uom = models.CharField(max_length=50, null=True, blank=True, verbose_name="UOM")
    volume = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Volume")
    weight = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Weight")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Unit Price")

    class Meta:
        db_table = 'wms_outbound_order_item'
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.order.order_number} - {self.sku.part_number} (Qty: {self.qty})"

class OrderCharge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(OutboundOrder, on_delete=models.CASCADE, related_name='charges', verbose_name="Order")
    origin = models.CharField(max_length=100, null=True, blank=True, verbose_name="Charge Origin")
    category = models.CharField(max_length=100, null=True, blank=True, verbose_name="Category")
    label = models.CharField(max_length=255, null=True, blank=True, verbose_name="Label")
    per_unit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Price Per Unit")
    units = models.IntegerField(null=True, blank=True, verbose_name="Units")
    total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total")

    class Meta:
        db_table = 'wms_order_charge'
        verbose_name = "Order Charge"
        verbose_name_plural = "Order Charges"

    def __str__(self):
        return f"{self.order.order_number} Charge - {self.label}"