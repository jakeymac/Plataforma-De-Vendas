# Generated by Django 5.0.3 on 2024-04-26 04:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Stores', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='products',
        ),
    ]
