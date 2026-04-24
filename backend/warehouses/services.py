from django.db import transaction
from django.db.models import F, Sum
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
        Outbound Logic: Complex multi-bin deduction algorithm with atomic locking.
        """
        order = Order.objects.select_for_update().filter(transaction_id=order_key).first()
        if not order:
            order = Order.objects.select_for_update().filter(id=order_key).first()
        if not order:
            raise ValueError("Order not found.")
        
        if order.status in ['SHIPPED', 'COMPLETE']:
            raise ValueError("Order has already been completed.")

        order_items = order.items.all()
        
        for item in order_items:
            remaining_to_deduct = item.qty
            
            # Find all bins containing this SKU, sorted by quantity descending
            # Using select_for_update() to prevent race conditions during shipping
            stock_records = Inventory.objects.select_for_update().filter(
                sku_id=item.sku_id,
                qty__gt=0
            ).order_by('-qty')

            total_available = stock_records.aggregate(total=Sum('qty'))['total'] or 0
            
            if total_available < item.qty:
                raise ValueError(
                    f"Insufficient stock for SKU: {item.sku.part_number}. "
                    f"Required: {item.qty}, Available: {total_available}"
                )

            for record in stock_records:
                if remaining_to_deduct <= 0:
                    break

                deduct_now = min(record.qty, remaining_to_deduct)
                
                # Update inventory record
                record.qty = F('qty') - deduct_now
                record.save()

                # Create audit trail for each bin deduction
                InventoryTransaction.objects.create(
                    type='OUTBOUND',
                    sku_id=item.sku_id,
                    client_id=order.client_id,
                    change_qty=-deduct_now,
                    from_bin_id=record.bin_id,
                    reference_id=order.transaction_id or order.order_number,
                    reason='ORDER_FULFILLMENT'
                )

                remaining_to_deduct -= deduct_now

        # Finalize order status
        order.status = 'COMPLETE'
        order.save()
        return order

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