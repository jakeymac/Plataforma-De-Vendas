# Generated by Django 5.0.3 on 2024-11-07 06:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0018_topsubcategory'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TopSubcategory',
            new_name='ProductTopSubcategory',
        ),
    ]
