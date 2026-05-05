import uuid
import zoneinfo
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

TIMEZONE_CHOICES = sorted([(tz, tz) for tz in zoneinfo.available_timezones()])

class Country(models.Model):
    code = models.CharField(max_length=10, primary_key=True) # 如 'US', 'CA', 'MX'
    name = models.CharField(max_length=100) # 如 'United States', 'Mexico'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

class Region(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')
    code = models.CharField(max_length=10) # 如 'NY', 'CDMX'
    name = models.CharField(max_length=100) # 如 'New York', 'Ciudad de México'

    class Meta:
        unique_together = ('country', 'code')
        verbose_name = "State/Province"
        verbose_name_plural = "States/Provinces"

    def __str__(self):
        return f"{self.name} ({self.country.code})"

class CountryTimezone(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='timezones')
    timezone_id = models.CharField(max_length=100) # America/New_York
    display_name = models.CharField(max_length=100) # Eastern Time
    class Meta:
        unique_together = ('country', 'timezone_id')
        verbose_name = "Country Timezone"
        verbose_name_plural = "Country Timezones"
    def __str__(self): return f"{self.display_name} ({self.country.code})"
    
class Client(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        INACTIVE = 'INACTIVE', _('Inactive')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Company Name")
    alias_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="Alias/External ID")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, verbose_name="Status")
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name="Phone Number")
    fax = models.CharField(max_length=50, null=True, blank=True, verbose_name="Fax Number")
    website = models.URLField(max_length=255, null=True, blank=True, verbose_name="Website")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Country")
    
    address1 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 1")
    address2 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 2")
    
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name="State/Province")
    
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="City/Township")
    postal_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Zip/Postal")
    contact_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Primary Contact Name")
    contact_phone = models.CharField(max_length=50, null=True, blank=True, verbose_name="Primary Contact Phone")
    contact_email = models.EmailField(null=True, blank=True, verbose_name="Primary Contact Email")
    warehouses = models.ManyToManyField('Warehouse', related_name='clients', blank=True, verbose_name="Accessible Warehouses")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'wms_client'
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        if self.state and self.country:
            exists = Region.objects.filter(country=self.country, code=self.state).exists()
            if not exists:
                raise ValidationError({'state': _(f'Invalid state code "{self.state}" for selected country.')})

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
    
    # 动态国家（外键）
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Country")
    
    # 州/省（通过 JS 异步联动）
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name="State/Province")
    
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="City")
    postal_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Postal Code")
    
    # 【标准化修改】改为带 choices 的 CharField
    time_zone = models.CharField(
        max_length=100, 
        choices=TIMEZONE_CHOICES, 
        default='UTC', 
        null=True, 
        blank=True, 
        verbose_name="Time Zone"
    )
    
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

    def clean(self):
        super().clean()
        # 校验州/省的合法性
        if self.state and self.country:
            exists = Region.objects.filter(country=self.country, code=self.state).exists()
            if not exists:
                raise ValidationError({'state': _(f'Invalid state code "{self.state}" for selected country.')})
        
        # [新增] 校验时区的合法性
        if self.time_zone and self.time_zone not in zoneinfo.available_timezones():
            raise ValidationError({'time_zone': _('Invalid IANA Time Zone.')})

class Location(models.Model):
    class TypeChoices(models.TextChoices):
        STORAGE = 'STORAGE', _('Storage location')
        STAGING = 'STAGING', _('Staging location')
        PUTAWAY = 'PUTAWAY', _('Put-away vehicle')
        QUARANTINE = 'QUARANTINE', _('Quarantine')
        PICKLINE = 'PICKLINE', _('PickLine')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Location ID")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.RESTRICT, related_name='locations', null=True, blank=True, verbose_name="Warehouse")
    type = models.CharField(max_length=50, choices=TypeChoices.choices, default=TypeChoices.STORAGE, verbose_name="Location Type Identifier")
    zone = models.CharField(max_length=100, null=True, blank=True, verbose_name="Location Zone")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Location Description")
    pick_path = models.IntegerField(default=0, verbose_name="Pick Path")
    is_non_pickable = models.BooleanField(default=False, verbose_name="Non-pickable")
    width = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Width")
    length = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Length")
    height = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Height")
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Max Weight")
    min_temperature = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Min Temperature")
    min_quantity = models.IntegerField(default=0, verbose_name="Min Quantity")
    allocation_priority = models.IntegerField(default=10, verbose_name="Allocation Priority")
    billing_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Billing Type")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        db_table = 'wms_location'
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"

class Sku(models.Model):
    """
    Represents a Stock Keeping Unit (SKU). 
    This is the master data for products within the WMS, scoped by Client.
    """

    # --- Choice Classes ---
    class TrackingMethod(models.TextChoices):
        NONE = 'NONE', 'No Tracking'
        BATCH = 'BATCH', 'Batch/Lot Tracking'
        SERIAL = 'SERIAL', 'Serial Number Tracking'

    class StorageCondition(models.TextChoices):
        AMBIENT = 'AMBIENT', 'Ambient/Normal'
        CHILLED = 'CHILLED', 'Chilled/Cold'
        FROZEN = 'FROZEN', 'Frozen'
        HAZMAT = 'HAZMAT', 'Hazardous Material'

    # 【新增】分配策略选项
    class AllocationMethod(models.TextChoices):
        FIFO = 'FIFO', 'First In First Out (Earliest Received First)'
        FEFO = 'FEFO', 'First Expired First Out (Earliest Expiry First)'
        PICKPATH = 'PICKPATH', 'Shortest Pick Path (Nearest Location First)'

    # --- Identity & Ownership ---
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        'Client', 
        on_delete=models.CASCADE, 
        related_name='skus', 
        verbose_name="Client/Owner"
    )
    part_number = models.CharField(
        max_length=100, 
        db_index=True, 
        verbose_name="Part Number (SKU Code)"
    )
    barcode = models.CharField(
        max_length=100, 
        db_index=True, 
        null=True, 
        blank=True, 
        verbose_name="Primary Barcode"
    )
    name = models.CharField(max_length=255, verbose_name="Product Name")
    description = models.TextField(null=True, blank=True, verbose_name="Technical Specification")

    # --- Physical Dimensions (Metric System) ---
    length = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, 
        verbose_name="Length (mm)", help_text="Unit: Millimeters"
    )
    width = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, 
        verbose_name="Width (mm)"
    )
    height = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, 
        verbose_name="Height (mm)"
    )
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, default=0, 
        verbose_name="Gross Weight (kg)", help_text="Unit: Kilograms"
    )
    volume = models.DecimalField(
        max_digits=15, decimal_places=4, default=0, 
        verbose_name="Volume (mm³)", help_text="Calculated as L*W*H"
    )

    # --- Inventory Policy & Traceability ---
    track_by = models.CharField(
        max_length=20, 
        choices=TrackingMethod.choices, 
        default=TrackingMethod.NONE,
        verbose_name="Tracking Method"
    )
    uom = models.CharField(
        max_length=20, 
        default="EA", 
        verbose_name="Unit of Measure", 
        help_text="e.g., EA (Each), CS (Case), PL (Pallet)"
    )
    
    # Expiry and Shelf Life Logic
    is_expiry_managed = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(
        default=0, 
        verbose_name="Shelf Life (Days)"
    )
    min_inbound_shelf_life_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Min Inbound Life %",
        help_text="Reject if remaining shelf life is below this percentage"
    )

    # 【新增】将分配策略绑定到 SKU 上，默认为 FIFO
    allocation_method = models.CharField(
        max_length=20,
        choices=AllocationMethod.choices,
        default=AllocationMethod.FIFO,
        verbose_name="Allocation Strategy"
    )

    # --- Warehouse Operations ---
    storage_condition = models.CharField(
        max_length=20, 
        choices=StorageCondition.choices, 
        default=StorageCondition.AMBIENT
    )
    is_fragile = models.BooleanField(default=False)
    abc_analysis = models.CharField(
        max_length=1, 
        choices=[('A', 'High Velocity'), ('B', 'Medium'), ('C', 'Low')],
        default='B'
    )

    # --- Audit & Control ---
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wms_sku'
        unique_together = ('client', 'part_number')
        verbose_name = "SKU"
        verbose_name_plural = "SKUs"
        indexes = [
            models.Index(fields=['client', 'barcode']),
            models.Index(fields=['part_number']),
        ]

    def save(self, *args, **kwargs):
        self.volume = Decimal(self.length) * Decimal(self.width) * Decimal(self.height)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client.name} | {self.part_number}"

class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.ForeignKey(Sku, on_delete=models.RESTRICT, related_name='inventory', verbose_name="SKU")
    bin = models.ForeignKey(Location, on_delete=models.RESTRICT, related_name='inventory', verbose_name="Bin Location")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='inventory', verbose_name="Client")
    qty = models.IntegerField(default=0, verbose_name="Quantity")
    serial_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Serial Number")
    lot_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Lot Number")
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name="Expiry Date")
    
    # 【新增】记录该批库存首次入库的时间，用于 FIFO 计算
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At / Receipt Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'wms_inventory'
        unique_together = ('sku', 'bin', 'serial_number', 'lot_number')
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory Records"

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
    change_qty = models.IntegerField(verbose_name="Quantity Changed")
    from_bin = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_from', verbose_name="From Bin")
    to_bin = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions_to', verbose_name="To Bin")
    reference_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Reference ID")
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="Reason")
    serial_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Serial Number")
    lot_number = models.CharField(max_length=255, null=True, blank=True, verbose_name="Lot Number")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")

    class Meta:
        db_table = 'wms_inventory_transaction'
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        SHIPPED = 'SHIPPED', _('Shipped')
        COMPLETE = 'COMPLETE', _('Complete')
        CLOSED = 'CLOSED', _('Closed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='orders', verbose_name="Customer")
    warehouse = models.ForeignKey('Warehouse', on_delete=models.RESTRICT, related_name='orders', null=True, blank=True, verbose_name="Warehouse")
    
    order_number = models.CharField(max_length=100, unique=True, verbose_name="Reference Number")    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Transaction ID")
    purchase_order = models.CharField(max_length=100, null=True, blank=True, verbose_name="Purchase Order")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name="Status")
    earliest_ship_date = models.DateTimeField(null=True, blank=True, verbose_name="Earliest Ship Date")
    ship_cancel_date = models.DateTimeField(null=True, blank=True, verbose_name="Ship Cancel Date")
    created_by = models.CharField(max_length=100, null=True, blank=True, verbose_name="Created By")

    recipient_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Recipient Name")
    company_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Company Name")
    phone = models.CharField(max_length=50, null=True, blank=True, verbose_name="Phone")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    address1 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 1")
    address2 = models.CharField(max_length=255, null=True, blank=True, verbose_name="Address 2")
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Country")
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name="State/Province")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="City/Township")
    postal_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="Zip/Postal")
    
    retailer_id = models.CharField(max_length=100, null=True, blank=True, verbose_name="Retailer ID")
    department_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Department Number")

    carrier = models.CharField(max_length=100, null=True, blank=True, verbose_name="Carrier")
    scac = models.CharField(max_length=50, null=True, blank=True, verbose_name="SCAC")
    service = models.CharField(max_length=100, null=True, blank=True, verbose_name="Service")
    billing_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Billing Type")
    account_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Account Number")
    account_zip = models.CharField(max_length=50, null=True, blank=True, verbose_name="Account Zip/Postal")
    tracking_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Tracking Number")
    warehouse_instructions = models.TextField(null=True, blank=True, verbose_name="Warehouse Instructions")
    carrier_instructions = models.TextField(null=True, blank=True, verbose_name="Carrier Instructions")
    
    load_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Load Number")
    bol_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="BOL Number")
    trailer_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Trailer Number")
    seal_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Seal Number")
    door = models.CharField(max_length=50, null=True, blank=True, verbose_name="Door")
    capacity_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Capacity Type")
    pickup_date = models.DateTimeField(null=True, blank=True, verbose_name="Pickup Date/Time")

    require_return_receipt = models.BooleanField(default=False, verbose_name="Require return receipt")
    saturday_delivery = models.BooleanField(default=False, verbose_name="Saturday delivery")
    residential_delivery = models.BooleanField(default=False, verbose_name="Residential delivery")
    insurance = models.BooleanField(default=False, verbose_name="Insurance")
    insurance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Insurance Amount")
    
    total_packages = models.IntegerField(default=0, verbose_name="Total Packages")
    packaging_uom = models.CharField(max_length=50, null=True, blank=True, verbose_name="Packaging UOM")
    total_weight = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name="Total Weight lbs")
    total_movable_units = models.IntegerField(default=0, verbose_name="Total Movable Units")
    mu_uom = models.CharField(max_length=50, null=True, blank=True, verbose_name="Movable Unit UOM")
    total_volume = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name="Total Volume cu ft")
    cancel_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wms_order'
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"{self.order_number} ({self.client.name})"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sku = models.ForeignKey('Sku', on_delete=models.RESTRICT, related_name='order_items')
    qty = models.IntegerField(verbose_name="Quantity")
    uom = models.CharField(max_length=50, default="Each", verbose_name="Primary Units")
    volume = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'wms_order_item'

class Receipt(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        COMPLETE = 'COMPLETE', _('Complete')
        RECEIVED = 'RECEIVED', _('Received')
        CLOSED = 'CLOSED', _('Closed')
        CANCELLED = 'CANCELLED', _('Canceled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.OPEN, verbose_name="Status")
    
    # [FIX] Also added null=True to Receipt transaction_id to prevent potential next error
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name="Transaction ID")
    
    reference_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Reference Number")
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='receipts', verbose_name="Customer")
    warehouse = models.ForeignKey('Warehouse', on_delete=models.RESTRICT, related_name='receipts', null=True, blank=True, verbose_name="Warehouse")
    arrival_date = models.DateTimeField(null=True, blank=True, verbose_name="Arrival Date")
    expected_arrival_date = models.DateTimeField(null=True, blank=True, verbose_name="Expected Arrival Date")
    trailer_pro_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Trailer/Pro Number")
    purchase_order_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Purchase Order Number")
    receipt_advice_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Receipt Advice Number")
    notes = models.TextField(null=True, blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wms_receipt'
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"

    def __str__(self):
        return f"{self.transaction_id} ({self.client.name})"

class ReceiptItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    sku = models.ForeignKey('Sku', on_delete=models.RESTRICT, related_name='receipt_items')
    qty = models.IntegerField(verbose_name="Qty (Pallet)")
    weight_lbs = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    lot_number = models.CharField(max_length=100, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    mu_label = models.CharField(max_length=100, null=True, blank=True, verbose_name="MU Label")
    split_mu = models.BooleanField(default=False)
    primary_units_per_mu = models.IntegerField(null=True, blank=True)
    mu_type = models.CharField(max_length=100, null=True, blank=True)
    length_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mu_weight_lbs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    putaway_location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True, blank=True)
    is_on_hold = models.BooleanField(default=False)
    custom_fields = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'wms_receipt_item'