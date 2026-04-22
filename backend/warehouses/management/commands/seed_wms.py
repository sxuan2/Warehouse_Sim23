from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from warehouses.models import (
    Client, Warehouse, Location, Sku, Inventory, 
    InventoryTransaction, OutboundOrder, OutboundOrderItem, OrderCharge
)

class Command(BaseCommand):
    help = 'Seeds the database with initial WMS data (Clients, Warehouses, SKUs, Inventory, Orders)'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('>>> DATA_OPS: CLEANING EXISTING DATA'))
        
        # Delete in reverse order of dependencies to avoid foreign key constraint errors
        OrderCharge.objects.all().delete()
        OutboundOrderItem.objects.all().delete()
        OutboundOrder.objects.all().delete()
        InventoryTransaction.objects.all().delete()
        Inventory.objects.all().delete()
        Sku.objects.all().delete()
        Location.objects.all().delete()
        Warehouse.objects.all().delete()
        Client.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('>>> DATA_OPS: CREATING NEW SEED DATA'))

        # 1. Create Client
        client = Client.objects.create(name='MAD BARN INC.')

        # 2. Create Warehouses
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
            email='ops.calgary@example.com',
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

        # 3. Create Locations (Bins)
        locs = [
            Location.objects.create(name='A-10-01', zone='Pick', type='PICKING', warehouse=calgary_wh),
            Location.objects.create(name='A-10-02', zone='Pick', type='PICKING', warehouse=calgary_wh),
            Location.objects.create(name='B-20-01', zone='Bulk', type='BULK', warehouse=calgary_wh),
            Location.objects.create(name='L-01-01', zone='Pick', type='PICKING', warehouse=langley_wh)
        ]

        # 4. Create SKUs
        skus_data = [
            {'part_number': '628055180036', 'description': 'Omneity - Equine Mineral and Vitamin Premix - 25 kg', 'weight': 25.0, 'volume': 0.1412},
            {'part_number': '628055180043', 'description': 'Omneity - Equine Mineral and Vitamin Premix - 5 kg', 'weight': 5.0, 'volume': 21.7014},
            {'part_number': '628055180135', 'description': 'Omneity - Equine Mineral and Vitamin Pellet', 'weight': 20.0, 'volume': 262.5},
            {'part_number': '628055180159', 'description': 'Optimum Probiotics - 60 GRAM', 'weight': 0.06, 'volume': 1.8337},
            {'part_number': '628055180166', 'description': 'Optimum Probiotics - 0.5 kg 40/case', 'weight': 0.5, 'volume': 0.6562},
            {'part_number': '628055180197', 'description': 'Visceral+ - 5 kg', 'weight': 5.0, 'volume': 21.7014},
        ]

        created_skus = []
        for s_data in skus_data:
            sku = Sku.objects.create(
                client=client,
                part_number=s_data['part_number'],
                description=s_data['description']
            )
            created_skus.append({'sku': sku, 'weight': s_data['weight'], 'volume': s_data['volume']})

        # 5. Populate Inventory for each SKU in the Pick Bin
        for s_dict in created_skus:
            sku = s_dict['sku']
            Inventory.objects.create(
                sku=sku,
                bin=locs[0], # Place in first Pick bin (A-10-01)
                client=client,
                qty=1000,
                serial_number=f"SN-{sku.part_number[-4:]}-001"
            )

        # 6. Create a Sample Outbound Order
        order_number = "20260417-online orders"
        
        # Ensure timezone-aware datetime
        ship_date = timezone.make_aware(datetime(2026, 4, 17, 12, 0, 0))

        order = OutboundOrder.objects.create(
            order_number=order_number,
            client=client,
            status='PENDING',
            customer_name='MAD BARN INC.',
            warehouse_name='Calgary Warehouse',
            transaction_id='53684',
            purchase_order='PO-99120',
            earliest_ship_date=ship_date,
            contact_code='MADBONKITA',
            recipient_name='MAD BARN INC.',
            address1='1465 STRASBURG ROAD',
            city='KITCHENER',
            state='Ontario',
            country='Canada',
            postal_code='N2R 1H2',
            total_weight=1483.1506,
            total_volume=558.1713
        )

        # 7. Add Order Items to the Sample Order
        for idx in range(3):
            sku_dict = created_skus[idx]
            OutboundOrderItem.objects.create(
                order=order,
                sku=sku_dict['sku'],
                qty=(idx + 1) * 4,
                uom='Bag',
                weight=sku_dict['weight'],
                volume=sku_dict['volume'],
                price=45.0
            )

        self.stdout.write(self.style.SUCCESS('>>> SYSTEM_DB_TABLES POPULATED SUCCESSFULLY'))