# Generated by Django 5.0.3 on 2024-10-18 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0016_alter_productcategory_top_subcategories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productcategory',
            name='top_subcategories',
        ),
        migrations.AddField(
            model_name='productcategory',
            name='top_subcategories_products',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
