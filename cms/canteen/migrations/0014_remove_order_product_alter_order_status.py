# Generated by Django 4.2.6 on 2023-11-07 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0013_alter_order_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Delivered', 'Delivered'), ('Pending', 'Pending')], max_length=200, null=True),
        ),
    ]
