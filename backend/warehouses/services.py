from django.db import transaction
from django.db.models import F, Sum
# from django.db.models.functions import Coalesce
from .models import Inventory, InventoryTransaction, Order, Sku, Location, Receipt

class InventoryService:
    @staticmethod
    @transaction.atomic
    def receive_stock(sku_id, bin_id, qty, client_id, reason="MANUAL_RECEIPT"):
        """
        Inbound Logic: Atomic UPSERT for inventory and transaction logging.
        """
        if qty <= 0:
            raise ValueError("Quantity must be greater than zero.")

        # Find or create inventory record
        inventory, created = Inventory.objects.select_for_update().get_or_create(
            sku_id=sku_id,
            bin_id=bin_id,
            client_id=client_id,
            defaults={'qty': 0}
        )
        
        # Increment quantity
        inventory.qty = F('qty') + qty
        inventory.save()

        # Log the transaction
        return InventoryTransaction.objects.create(
            type='INBOUND',
            sku_id=sku_id,
            client_id=client_id,
            change_qty=qty,
            to_bin_id=bin_id,
            reason=reason
        )

class OrderService:
    @staticmethod
    @transaction.atomic
    def fulfill_order(order_key):
        """
        Outbound Logic: Multi-bin deduction algorithm powered by SKU-specific Allocation Strategy.
        Supports: FIFO, FEFO, PICKPATH with automatic fallback.
        """
        # 1. 查找并锁定订单
        order = Order.objects.select_for_update().filter(transaction_id=order_key).first()
        if not order:
            order = Order.objects.select_for_update().filter(id=order_key).first()
        if not order:
            raise ValueError("Order not found.")
        
        if order.status in ['SHIPPED', 'COMPLETE']:
            raise ValueError("Order has already been completed.")

        order_items = order.items.select_related('sku').all()
        
        for item in order_items:
            remaining_to_deduct = item.qty
            sku = item.sku
            method = sku.allocation_method
            
            # 2. 查找可用库存（锁定以防止并发发货冲突）
            base_query = Inventory.objects.select_for_update().filter(
                sku_id=sku.id,
                bin__warehouse=order.warehouse,
                qty__gt=0
            ).select_related('bin')

            # 3. 校验总库存是否充足
            total_available = base_query.aggregate(total=Sum('qty'))['total'] or 0
            if total_available < item.qty:
                raise ValueError(
                    f"Insufficient stock for SKU: {sku.part_number} in {order.warehouse.name}. "
                    f"Required: {item.qty}, Available: {total_available}"
                )

            # 4. 根据 SKU 的分配策略应用不同的排序规则
            if method == Sku.AllocationMethod.FEFO:
                # FEFO (先过期先出)：优先找有过期日期的且最早过期的。
                # Coalesce 技巧: 如果没有 expiry_date，将其排到最后面（按 FIFO 兜底）
                # 排序字段加入 bin__pick_path 作为第二优先级，同等保质期离得近先拿
                stock_records = base_query.order_by(
                    F('expiry_date').asc(nulls_last=True),
                    'created_at',
                    'bin__pick_path'
                )

            elif method == Sku.AllocationMethod.PICKPATH:
                # PICKPATH (最短路径优先)：直接按照 Location 表里的 pick_path 排序
                # 第二优先级为 FIFO
                stock_records = base_query.order_by(
                    'bin__pick_path',
                    'created_at'
                )

            else: 
                # FIFO (默认)：最早入库的先出
                # 第二优先级为 pick_path
                stock_records = base_query.order_by(
                    'created_at',
                    'bin__pick_path'
                )

            # 5. 执行逐步扣减逻辑
            for record in stock_records:
                if remaining_to_deduct <= 0:
                    break

                # 决定当前库位扣多少 (要么全拿走，要么拿够剩下的)
                deduct_now = min(record.qty, remaining_to_deduct)
                
                # 扣除库存
                record.qty = F('qty') - deduct_now
                record.save()

                # 创建审计日志 (Transaction)
                strategy_tag = f"[{method}] " # 可以在日志里标记是按什么策略出的货
                InventoryTransaction.objects.create(
                    type='OUTBOUND',
                    sku_id=sku.id,
                    client_id=order.client_id,
                    change_qty=-deduct_now,
                    from_bin_id=record.bin_id,
                    reference_id=order.transaction_id or order.order_number,
                    reason=f"{strategy_tag}ORDER_FULFILLMENT"
                )

                remaining_to_deduct -= deduct_now

        # 6. 更新订单状态
        order.status = 'COMPLETE'
        order.save()
        return order

    #[cite: 1] 下方的 reverts 和 ship_order 保持不变
    @staticmethod
    @transaction.atomic
    def revert_to_pending(order_key):
        order = Order.objects.select_for_update().filter(transaction_id=order_key).first()
        if not order:
            order = Order.objects.select_for_update().filter(id=order_key).first()
        if not order:
            raise ValueError("Order not found.")

        if order.status not in ['COMPLETE', 'SHIPPED']:
            raise ValueError("Only completed orders can be reverted to pending.")

        order.status = 'PENDING'
        order.save(update_fields=['status', 'updated_at'])
        return order

    @staticmethod
    @transaction.atomic
    def ship_order(order_key):
        order = Order.objects.select_for_update().filter(transaction_id=order_key).first()
        if not order:
            order = Order.objects.select_for_update().filter(id=order_key).first()
        if not order:
            raise ValueError("Order not found.")

        if order.status != 'COMPLETE':
            raise ValueError("Only COMPLETE orders can be marked as SHIPPED.")

        order.status = 'SHIPPED'
        order.save(update_fields=['status', 'updated_at'])
        return order

class ReceiptService:
    @staticmethod
    def _resolve_receipt(receipt_key):
        receipt = Receipt.objects.select_for_update().filter(transaction_id=receipt_key).first()
        if not receipt:
            receipt = Receipt.objects.select_for_update().filter(id=receipt_key).first()
        if not receipt:
            raise ValueError("Receipt not found.")
        return receipt

    @staticmethod
    def _get_target_bin(receipt, item):
        target_bin = item.putaway_location
        if target_bin:
            return target_bin

        wh_code = receipt.warehouse.code if receipt.warehouse and receipt.warehouse.code else 'GEN'
        target_bin, _ = Location.objects.get_or_create(
            warehouse=receipt.warehouse,
            name=f"RECV-DOCK-{wh_code}",
            defaults={'type': Location.TypeChoices.STAGING}
        )
        return target_bin

    @staticmethod
    def _post_inventory(receipt):
        for item in receipt.items.select_related('sku', 'putaway_location').all():
            target_bin = ReceiptService._get_target_bin(receipt, item)

            inv, _ = Inventory.objects.select_for_update().get_or_create(
                sku=item.sku,
                bin=target_bin,
                client=receipt.client,
                lot_number=item.lot_number,
                defaults={'qty': 0}
            )
            inv.qty += item.qty
            if item.expiration_date:
                inv.expiry_date = item.expiration_date
            inv.save()

            InventoryTransaction.objects.create(
                type=InventoryTransaction.TypeChoices.INBOUND,
                sku=item.sku,
                client=receipt.client,
                change_qty=item.qty,
                to_bin=target_bin,
                reference_id=f"RECV-{receipt.transaction_id}",
                reason="Receipt Marked RECEIVED",
                lot_number=item.lot_number
            )

    @staticmethod
    def _unpost_inventory(receipt):
        for item in receipt.items.select_related('sku', 'putaway_location').all():
            target_bin = ReceiptService._get_target_bin(receipt, item)

            inv = Inventory.objects.select_for_update().filter(
                sku=item.sku,
                bin=target_bin,
                client=receipt.client,
                lot_number=item.lot_number,
            ).first()
            if not inv or inv.qty < item.qty:
                raise ValueError(f"Cannot revert receipt {receipt.transaction_id}: insufficient on-hand for SKU {item.sku.part_number}.")

            inv.qty -= item.qty
            inv.save()

            InventoryTransaction.objects.create(
                type=InventoryTransaction.TypeChoices.ADJUSTMENT,
                sku=item.sku,
                client=receipt.client,
                change_qty=-item.qty,
                from_bin=target_bin,
                reference_id=f"RECV-{receipt.transaction_id}",
                reason="Receipt reverted from RECEIVED",
                lot_number=item.lot_number
            )

    @staticmethod
    @transaction.atomic
    def update_status(receipt_key, target_status):
        receipt = ReceiptService._resolve_receipt(receipt_key)

        current = receipt.status
        target = (target_status or '').upper().strip()
        if current == target:
            return receipt

        allowed = {
            Receipt.StatusChoices.OPEN: {Receipt.StatusChoices.COMPLETE},
            Receipt.StatusChoices.COMPLETE: {Receipt.StatusChoices.OPEN, Receipt.StatusChoices.RECEIVED},
            Receipt.StatusChoices.RECEIVED: {Receipt.StatusChoices.COMPLETE},
        }

        if target not in allowed.get(current, set()):
            raise ValueError(f"Invalid transition: {current} -> {target}")

        if current == Receipt.StatusChoices.COMPLETE and target == Receipt.StatusChoices.RECEIVED:
            ReceiptService._post_inventory(receipt)
        elif current == Receipt.StatusChoices.RECEIVED and target == Receipt.StatusChoices.COMPLETE:
            ReceiptService._unpost_inventory(receipt)

        receipt.status = target
        receipt.save(update_fields=['status'])
        return receipt