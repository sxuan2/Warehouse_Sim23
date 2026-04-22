from django.db import transaction
from django.db.models import F, Sum
from .models import Inventory, InventoryTransaction, OutboundOrder, Sku, Location

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
    def fulfill_order(order_id):
        """
        Outbound Logic: Complex multi-bin deduction algorithm with atomic locking.
        """
        order = OutboundOrder.objects.select_for_update().get(id=order_id)
        
        if order.status == 'SHIPPED':
            raise ValueError("Order has already been shipped.")

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
                    reference_id=order.order_number,
                    reason='ORDER_FULFILLMENT'
                )

                remaining_to_deduct -= deduct_now

        # Finalize order status
        order.status = 'SHIPPED'
        order.save()
        return order