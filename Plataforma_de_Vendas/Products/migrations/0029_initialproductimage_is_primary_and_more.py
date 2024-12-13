# Generated by Django 5.0.3 on 2024-12-13 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0028_initialproductimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='initialproductimage',
            name='is_primary',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productimage',
            name='is_primary',
            field=models.BooleanField(default=False),
        ),
    ]