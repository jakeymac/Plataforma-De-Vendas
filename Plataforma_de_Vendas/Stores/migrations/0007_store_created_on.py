# Generated by Django 5.0.3 on 2024-08-08 04:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stores', '0006_rename_description_store_store_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
