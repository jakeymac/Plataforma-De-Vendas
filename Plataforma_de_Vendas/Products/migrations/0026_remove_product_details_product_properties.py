# Generated by Django 5.0.3 on 2024-12-10 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0025_alter_productcategory_id_alter_productsubcategory_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='details',
        ),
        migrations.AddField(
            model_name='product',
            name='properties',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
