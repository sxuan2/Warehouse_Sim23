from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from warehouses.models import (
    Client, Warehouse, Location, Sku, Inventory, 
    InventoryTransaction, OutboundOrder, OutboundOrderItem, OrderCharge
)

class Command(BaseCommand):
    help = 'Seeds the database with detailed multi-client WMS data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> DATA_OPS: CLEANING EXISTING DATA'))
        
        OrderCharge.objects.all().delete()
        OutboundOrderItem.objects.all().delete()
        OutboundOrder.objects.all().delete()
        InventoryTransaction.objects.all().delete()
        Inventory.objects.all().delete()
        Sku.objects.all().delete()
        Location.objects.all().delete()
        Warehouse.objects.all().delete()
        Client.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('>>> DATA_OPS: CREATING NEW SEED DATA WITH MULTIPLE CLIENTS'))

        # --- 1. Create Multiple Clients ---
        
        # Client 1: Based strictly on the provided image
        client_mad_barn = Client.objects.create(
            name='MAD BARN INC.',
            alias_id='MADBONKITA',
            phone='833-623-2276',
            fax='',
            website='',
            email='',
            country='Canada',
            address1='1465 STRASBURG ROAD',
            address2='',
            state='Ontario',
            city='KITCHNER',
            postal_code='N2R 1H2',
            contact_name='Sadia SaiF',
            contact_phone='266-770-3997',
            contact_email=''
        )

        # Client 2: A dummy technology client
        client_techflow = Client.objects.create(
            name='TechFlow Logistics',
            alias_id='TECHFLOW_01',
            phone='1-800-555-0199',
            fax='1-800-555-0198',
            website='https://techflow-logistics.example.com',
            email='support@techflow.example.com',
            country='United States',
            address1='4000 Innovation Parkway',
            address2='Suite 200',
            state='California',
            city='San Jose',
            postal_code='95134',
            contact_name='Alexander Chen',
            contact_phone='408-555-0122',
            contact_email='achen@techflow.example.com'
        )

        # Client 3: A dummy global trading client
        client_global = Client.objects.create(
            name='Global Traders LLC',
            alias_id='GLB_TRD_LLC',
            phone='+44 20 7946 0958',
            fax='',
            website='https://global-traders.example.co.uk',
            email='operations@global-traders.example.co.uk',
            country='United Kingdom',
            address1='150 London Wall',
            address2='',
            state='Greater London',
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
            country='Canada',
            state='AB',
            city='S.E Calgary',
            postal_code='T2C 4X7',
            time_zone='(UTC-07:00) Mountain Time (Canada)',
            phone='403-555-1100',
            status='ACTIVE'
        )

        langley_wh = Warehouse.objects.create(
            name='Langley Warehouse',
            code='PCDL',
            zone='B',
            address1='27433 52nd Avenue',
            country='Canada',
            state='British Columbia',
            city='Langley',
            postal_code='V4W 4B2',
            time_zone='(UTC-08:00) Pacific Time (US & Canada)',
            phone='604-888-8489',
            status='ACTIVE'
        )

        # --- 3. Create Locations (Bins) ---
        loc_calg_pick_1 = Location.objects.create(name='A-10-01', zone='Pick', type='PICKING', warehouse=calgary_wh)
        loc_calg_pick_2 = Location.objects.create(name='A-10-02', zone='Pick', type='PICKING', warehouse=calgary_wh)
        loc_lang_bulk_1 = Location.objects.create(name='B-20-01', zone='Bulk', type='BULK', warehouse=langley_wh)

        # --- 4. Create SKUs for different clients ---
        
        # SKUs for MAD BARN
        sku_mb_1 = Sku.objects.create(client=client_mad_barn, part_number='628055180036', description='Omneity - Equine Mineral and Vitamin Premix - 25 kg')
        sku_mb_2 = Sku.objects.create(client=client_mad_barn, part_number='628055180159', description='Optimum Probiotics - 60 GRAM')

        # SKUs for TechFlow
        sku_tf_1 = Sku.objects.create(client=client_techflow, part_number='TF-GPU-4090', description='NVIDIA RTX 4090 Graphics Card')
        sku_tf_2 = Sku.objects.create(client=client_techflow, part_number='TF-SSD-2TB', description='2TB NVMe Solid State Drive')

        # SKUs for Global Traders
        sku_gl_1 = Sku.objects.create(client=client_global, part_number='GL-COF-001', description='Premium Arabica Coffee Beans - 1kg')

        # --- 5. Populate Inventory ---
        Inventory.objects.create(sku=sku_mb_1, bin=loc_calg_pick_1, client=client_mad_barn, qty=500, serial_number='SN-MB-001')
        Inventory.objects.create(sku=sku_mb_2, bin=loc_calg_pick_2, client=client_mad_barn, qty=1200, serial_number='SN-MB-002')
        Inventory.objects.create(sku=sku_tf_1, bin=loc_lang_bulk_1, client=client_techflow, qty=50, serial_number='SN-TF-4090-01')
        Inventory.objects.create(sku=sku_gl_1, bin=loc_calg_pick_1, client=client_global, qty=3000, lot_number='LOT-COF-2026')

        # --- 6. Create Orders ---
        ship_date = timezone.make_aware(datetime(2026, 4, 17, 12, 0, 0))

        order_mb = OutboundOrder.objects.create(
            order_number="20260417-MADBARN-01",
            client=client_mad_barn,
            status='PENDING',
            customer_name=client_mad_barn.name,
            warehouse_name='Calgary Warehouse',
            earliest_ship_date=ship_date,
            recipient_name=client_mad_barn.contact_name,
            address1=client_mad_barn.address1,
            city=client_mad_barn.city,
            state=client_mad_barn.state,
            country=client_mad_barn.country
        )
        OutboundOrderItem.objects.create(order=order_mb, sku=sku_mb_1, qty=10, uom='Bag', price=45.0)

        order_tf = OutboundOrder.objects.create(
            order_number="20260418-TECHFLOW-99",
            client=client_techflow,
            status='PROCESSING',
            customer_name=client_techflow.name,
            warehouse_name='Langley Warehouse',
            earliest_ship_date=ship_date,
            city='San Jose',
            country='United States'
        )
        OutboundOrderItem.objects.create(order=order_tf, sku=sku_tf_1, qty=2, uom='Box', price=1599.99)

        self.stdout.write(self.style.SUCCESS('>>> SYSTEM_DB_TABLES POPULATED SUCCESSFULLY'))