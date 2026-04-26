from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0002_receipt_status_received'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OutboundOrder',
            new_name='Order',
        ),
        migrations.RenameModel(
            old_name='OutboundOrderItem',
            new_name='OrderItem',
        ),
        migrations.AlterModelTable(
            name='order',
            table='wms_order',
        ),
        migrations.AlterModelTable(
            name='orderitem',
            table='wms_order_item',
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
    ]
