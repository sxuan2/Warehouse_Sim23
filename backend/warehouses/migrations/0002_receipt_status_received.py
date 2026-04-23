from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='status',
            field=models.CharField(
                choices=[
                    ('OPEN', 'Open'),
                    ('COMPLETE', 'Complete'),
                    ('RECEIVED', 'Received'),
                    ('CLOSED', 'Closed'),
                    ('CANCELLED', 'Canceled'),
                ],
                default='OPEN',
                max_length=20,
                verbose_name='Status',
            ),
        ),
    ]
