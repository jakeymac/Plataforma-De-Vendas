# Generated by Django 5.0.3 on 2024-04-26 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stores', '0002_remove_store_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='url',
            field=models.CharField(max_length=75),
        ),
    ]
