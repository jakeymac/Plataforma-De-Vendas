# Generated by Django 5.0.3 on 2024-11-23 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0022_remove_product_minimum_quantity_remove_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='draft',
            field=models.BooleanField(default=True),
        ),
    ]
