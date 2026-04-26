from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from warehouses.models import (
    Client, Country, Warehouse, Location, Sku, Inventory,
    InventoryTransaction, Order, OrderItem, Receipt, ReceiptItem
)

class Command(BaseCommand):
    help = 'Seeds the database with detailed multi-client WMS data'

    def _country(self, code: str, name: str):
        country, _ = Country.objects.get_or_create(code=code, defaults={'name': name})
        if country.name != name:
            country.name = name
            country.save(update_fields=['name'])
        return country

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> DATA_OPS: CLEANING EXISTING DATA'))
        
        ReceiptItem.objects.all().delete()
        Receipt.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        InventoryTransaction.objects.all().delete()
        Inventory.objects.all().delete()
        Sku.objects.all().delete()
        Location.objects.all().delete()
        Warehouse.objects.all().delete()
        Client.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('>>> DATA_OPS: CREATING NEW SEED DATA WITH MULTIPLE CLIENTS'))

        canada = self._country('CA', 'Canada')
        united_states = self._country('US', 'United States')
        united_kingdom = self._country('GB', 'United Kingdom')

        # --- 1. Create Multiple Clients ---
        
        client_mad_barn = Client.objects.create(
            name='MAD BARN INC.',
            alias_id='MADBONKITA',
            phone='833-623-2276',
            fax='',
            website='',
            email='',
            country=canada,
            address1='1465 STRASBURG ROAD',
            address2='',
            state='ON',
            city='KITCHNER',
            postal_code='N2R 1H2',
            contact_name='Sadia SaiF',
            contact_phone='266-770-3997',
            contact_email=''
        )

        client_techflow = Client.objects.create(
            name='TechFlow Logistics',
            alias_id='TECHFLOW_01',
            phone='1-800-555-0199',
            fax='1-800-555-0198',
            website='https://techflow-logistics.example.com',
            email='support@techflow.example.com',
            country=united_states,
            address1='4000 Innovation Parkway',
            address2='Suite 200',
            state='CA',
            city='San Jose',
            postal_code='95134',
            contact_name='Alexander Chen',
            contact_phone='408-555-0122',
            contact_email='achen@techflow.example.com'
        )

        client_global = Client.objects.create(
            name='Global Traders LLC',
            alias_id='GLB_TRD_LLC',
            phone='+44 20 7946 0958',
            fax='',
            website='https://global-traders.example.co.uk',
            email='operations@global-traders.example.co.uk',
            country=united_kingdom,
            address1='150 London Wall',
            address2='',
            state='ENG',
            city='London',
            postal_code='EC2Y 5HN',
            contact_name='Sarah Jenkins',
            contact_phone='+44 7700 900077',
            contact_email='s.jenkins@global-traders.example.co.uk'
        )

        # --- 2. Create Warehouses ---
        calgary_wh = Warehouse.objects.create(
            name='Calgary Warehouse',
            code='CALG',
            zone='A',
            address1='510 Carmek Blvd.',
            country=canada,
            state='AB',
            city='S.E Calgary',
            postal_code='T2C 4X7',
            time_zone='America/Edmonton',
            phone='403-555-1100',
            status='ACTIVE'
        )

        langley_wh = Warehouse.objects.create(
            name='Langley Warehouse',
            code='PCDL',
            zone='B',
            address1='27433 52nd Avenue',
            country=canada,
            state='BC',
            city='Langley',
            postal_code='V4W 4B2',
            time_zone='America/Vancouver',
            phone='604-888-8489',
            status='ACTIVE'
        )

        # --- 3. Create Locations (Bins) ---
        loc_calg_pick_1 = Location.objects.create(name='A-10-01', zone='Pick', type='PICKLINE', warehouse=calgary_wh)
        loc_calg_pick_2 = Location.objects.create(name='A-10-02', zone='Pick', type='PICKLINE', warehouse=calgary_wh)
        loc_lang_bulk_1 = Location.objects.create(name='B-20-01', zone='Bulk', type='STORAGE', warehouse=langley_wh)

        # --- 4. Create SKUs for different clients ---

        sku_mb_1 = Sku.objects.create(
            client=client_mad_barn,
            part_number='628055180036',
            name='Omneity Equine Mineral and Vitamin Premix 25kg',
            description='Omneity - Equine Mineral and Vitamin Premix - 25 kg'
        )
        sku_mb_2 = Sku.objects.create(
            client=client_mad_barn,
            part_number='628055180159',
            name='Optimum Probiotics 60g',
            description='Optimum Probiotics - 60 GRAM'
        )

        sku_tf_1 = Sku.objects.create(
            client=client_techflow,
            part_number='TF-GPU-4090',
            name='NVIDIA RTX 4090 Graphics Card',
            description='NVIDIA RTX 4090 Graphics Card'
        )
        sku_tf_2 = Sku.objects.create(
            client=client_techflow,
            part_number='TF-SSD-2TB',
            name='2TB NVMe Solid State Drive',
            description='2TB NVMe Solid State Drive'
        )

        sku_gl_1 = Sku.objects.create(
            client=client_global,
            part_number='GL-COF-001',
            name='Premium Arabica Coffee Beans 1kg',
            description='Premium Arabica Coffee Beans - 1kg'
        )

        # --- 5. Populate Inventory ---
        Inventory.objects.create(sku=sku_mb_1, bin=loc_calg_pick_1, client=client_mad_barn, qty=500, serial_number='SN-MB-001')
        Inventory.objects.create(sku=sku_mb_2, bin=loc_calg_pick_2, client=client_mad_barn, qty=1200, serial_number='SN-MB-002')
        Inventory.objects.create(sku=sku_tf_1, bin=loc_lang_bulk_1, client=client_techflow, qty=50, serial_number='SN-TF-4090-01')
        Inventory.objects.create(sku=sku_gl_1, bin=loc_calg_pick_1, client=client_global, qty=3000, lot_number='LOT-COF-2026')

        # --- 6. Create Orders ---
        ship_date = timezone.make_aware(datetime(2026, 4, 17, 12, 0, 0))

        order_mb = Order.objects.create(
            order_number="20260417-MADBARN-01",
            client=client_mad_barn,
            warehouse=calgary_wh,
            status='PENDING',
            earliest_ship_date=ship_date,
            recipient_name=client_mad_barn.contact_name,
            company_name=client_mad_barn.name,
            address1=client_mad_barn.address1,
            city=client_mad_barn.city,
            state=client_mad_barn.state,
            country=client_mad_barn.country.name,
            purchase_order='PO-20260417-001',
            tracking_number=''
        )
        OrderItem.objects.create(order=order_mb, sku=sku_mb_1, qty=10, uom='Bag', price=45.0)
        OrderItem.objects.create(order=order_mb, sku=sku_mb_2, qty=6, uom='Case', price=18.5)

        order_tf = Order.objects.create(
            order_number="20260418-TECHFLOW-99",
            client=client_techflow,
            warehouse=langley_wh,
            status='PROCESSING',
            earliest_ship_date=ship_date,
            recipient_name=client_techflow.contact_name,
            company_name=client_techflow.name,
            city='San Jose',
            country=client_techflow.country.name,
            purchase_order='PO-20260418-099'
        )
        OrderItem.objects.create(order=order_tf, sku=sku_tf_1, qty=2, uom='Box', price=1599.99)

        # --- 7. Create Receipts ---
        receipt = Receipt.objects.create(
            transaction_id='RCV-20260422-001',
            reference_number='ASN-10001',
            client=client_mad_barn,
            warehouse=calgary_wh,
            status='OPEN',
            arrival_date=ship_date,
            trailer_pro_number='PRO-778899',
            purchase_order_number='PO-20260417-001',
            notes='Sample inbound receipt for dashboard data.'
        )
        ReceiptItem.objects.create(receipt=receipt, sku=sku_mb_1, qty=12, lot_number='LOT-MB-2404', mu_label='MU-0001', putaway_location=loc_calg_pick_1)

        # --- 8. Create Transactions ---
        InventoryTransaction.objects.create(
            type='INBOUND',
            sku=sku_mb_1,
            client=client_mad_barn,
            change_qty=12,
            from_bin=None,
            to_bin=loc_calg_pick_1,
            reference_id=receipt.id,
            reason='Seed receipt'
        )
        InventoryTransaction.objects.create(
            type='OUTBOUND',
            sku=sku_tf_1,
            client=client_techflow,
            change_qty=-2,
            from_bin=loc_lang_bulk_1,
            to_bin=None,
            reference_id=order_tf.id,
            reason='Seed order'
        )

        self.stdout.write(self.style.SUCCESS('>>> SYSTEM_DB_TABLES POPULATED SUCCESSFULLY'))