# Generated by Django 4.2.6 on 2023-11-08 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0015_product_inventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]