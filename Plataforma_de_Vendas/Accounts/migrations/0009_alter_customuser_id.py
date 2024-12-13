# Generated by Django 5.0.3 on 2024-12-05 06:39

import Accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0008_alter_customuser_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.CharField(default=Accounts.models.generate_unique_id, editable=False, max_length=12, primary_key=True, serialize=False, unique=True),
        ),
    ]