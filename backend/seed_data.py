import os
import django
import random
from datetime import datetime, timedelta

# ==========================================================
# 配置区域：请将 'your_project_name' 替换为你包含 settings.py 的文件夹名
# ==========================================================
PROJECT_NAME = 'core' 

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{PROJECT_NAME}.settings')
    try:
        django.setup()
        print("Django environment initialized successfully.")
    except Exception as e:
        print(f"Error initializing Django: {e}")
        print("Check if PROJECT_NAME is correct and you are in the project root.")
        exit(1)

# 必须先执行初始化，才能导入模型
setup_django()

# 现在导入 Django 相关组件
from django.utils import timezone
from warehouses.models import (
    Country, Region, Warehouse, Location, 
    Client, Sku, Inventory, Order, OrderItem
)

def run_seed():
    print("--- Starting Full WMS Data Seeding (US & CA) ---")

    # 1. 基础国家数据 (US & Canada)
    us, _ = Country.objects.get_or_create(code='US', defaults={'name': 'United States'})
    ca, _ = Country.objects.get_or_create(code='CA', defaults={'name': 'Canada'})
    
    # 省份/州数据
    regions = [
        (us, 'NY', 'New York'), (us, 'CA', 'California'),
        (ca, 'ON', 'Ontario'), (ca, 'BC', 'British Columbia'),
    ]
    for country, r_code, r_name in regions:
        Region.objects.get_or_create(country=country, code=r_code, defaults={'name': r_name})

    # 2. 创建客户 (Clients)
    client_configs = [
        {"name": "TechNova Solutions", "alias": "TNS-01", "country": us, "state": "NY"},
        {"name": "Arctic Maple Retail", "alias": "AMR-02", "country": ca, "state": "ON"},
    ]
    clients = []
    for c in client_configs:
        obj, _ = Client.objects.get_or_create(
            name=c['name'],
            defaults={
                "alias_id": c['alias'], 
                "country": c['country'], 
                "state": c['state'], 
                "status": "ACTIVE",
                "email": f"contact@{c['alias'].lower()}.com"
            }
        )
        clients.append(obj)

    # 3. 创建仓库 (Warehouses)
    wh_configs = [
        {"name": "Empire State DC", "code": "NY-WH", "country": us, "state": "NY", "tz": "America/New_York"},
        {"name": "Great Lakes Hub", "code": "ON-WH", "country": ca, "state": "ON", "tz": "America/Toronto"},
    ]
    warehouses = []
    for w in wh_configs:
        obj, _ = Warehouse.objects.get_or_create(
            code=w['code'],
            defaults={
                "name": w['name'], 
                "country": w['country'], 
                "state": w['state'], 
                "time_zone": w['tz'],
                "status": "ACTIVE"
            }
        )
        warehouses.append(obj)

    # 4. 创建商品 (SKUs)
    sku_list = []
    for client in clients:
        for i in range(1, 4):
            sku_code = f"{client.alias_id}-SKU-{i:03d}"
            sku, _ = Sku.objects.get_or_create(
                client=client,
                part_number=sku_code,
                defaults={
                    "description": f"Standard Product {i} for {client.name}", 
                    "track_by": "NONE"
                }
            )
            sku_list.append(sku)
    print(f"Created {len(sku_list)} SKUs.")

    # 5. 创建库位与初始库存 (Locations & Inventory)
    for wh in warehouses:
        # 创建收货暂存区
        stage, _ = Location.objects.get_or_create(
            name=f"{wh.code}-STAGE-01", 
            defaults={"warehouse": wh, "type": "STAGING", "zone": "RECEIVING"}
        )
        
        # 创建存储位并放置库存
        for i in range(1, 5):
            loc_name = f"{wh.code}-A1-{i:02d}"
            loc, _ = Location.objects.get_or_create(
                name=loc_name,
                defaults={"warehouse": wh, "type": "STORAGE", "zone": "BULK", "max_weight": 2000}
            )
            
            # 随机挑选一个 SKU 放入该库位
            target_sku = random.choice(sku_list)
            Inventory.objects.get_or_create(
                sku=target_sku,
                bin=loc,
                client=target_sku.client,
                defaults={"qty": random.randint(50, 200)}
            )
    print("Locations and Inventory generated.")

    # 6. 创建出库单 (Sample Orders)
    for client in clients:
        for i in range(1, 3):
            order_num = f"ORD-{client.alias_id}-{random.randint(1000, 9999)}"
            order, created = Order.objects.get_or_create(
                order_number=order_num,
                defaults={
                    "client": client,
                    "warehouse": random.choice(warehouses),
                    "status": "PENDING",
                    "recipient_name": f"Recipient {i}",
                    "address1": f"{random.randint(100, 999)} Business Way",
                    "city": "Springfield",
                    "country": "US" if client.country.code == 'US' else "CA"
                }
            )
            
            if created:
                # 为订单添加 1-2 个随机明细
                client_skus = [s for s in sku_list if s.client == client]
                order_skus = random.sample(client_skus, k=min(len(client_skus), random.randint(1, 2)))
                for s in order_skus:
                    OrderItem.objects.create(
                        order=order,
                        sku=s,
                        qty=random.randint(1, 10),
                        price=random.uniform(10.0, 100.0)
                    )
    
    print("--- Full Data Seeding Completed Successfully ---")

if __name__ == "__main__":
    run_seed()