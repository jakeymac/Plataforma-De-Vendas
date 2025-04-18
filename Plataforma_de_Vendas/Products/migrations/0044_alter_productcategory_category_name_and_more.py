# Generated by Django 5.1.5 on 2025-04-02 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Products", "0043_alter_product_product_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productcategory",
            name="category_name",
            field=models.CharField(
                error_messages={"unique": "Category with this name already exists"},
                max_length=45,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="productsubcategory",
            name="subcategory_name",
            field=models.CharField(
                error_messages={"unique": "Subcategory with this name already exists"},
                max_length=45,
                unique=True,
            ),
        ),
    ]
