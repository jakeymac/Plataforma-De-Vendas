# Generated by Django 5.0.3 on 2024-11-23 07:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0021_remove_product_name_product_product_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='minimum_quantity',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
    ]
