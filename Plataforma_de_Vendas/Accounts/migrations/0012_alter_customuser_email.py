# Generated by Django 5.1.5 on 2025-02-13 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Accounts", "0011_alter_customuser_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                error_messages={"unique": "A user with that email already exists."},
                max_length=254,
                unique=True,
            ),
        ),
    ]
