# Generated by Django 5.1.5 on 2025-03-20 18:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Products", "0041_initialproductstate_prices_product_prices"),
    ]

    operations = [
        migrations.RenameField(
            model_name="initialproductimage",
            old_name="product",
            new_name="initial_product",
        ),
    ]
