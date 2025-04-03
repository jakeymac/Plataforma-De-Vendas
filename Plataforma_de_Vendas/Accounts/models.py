from core.models import UniqueIDModel
from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError, models


class CustomUser(AbstractUser, UniqueIDModel):
    def user_profile_picture_path(instance, filename):
        return f"profile_pictures/{instance.username}/{filename}"

    store = models.ForeignKey(
        "Stores.Store", on_delete=models.CASCADE, null=True, blank=True
    )  # For sellers to have a store
    stock_notifications = models.BooleanField(
        default=True, null=True, blank=True
    )  # For sellers to receive notifcations of their stock levels.

    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(
        unique=True, error_messages={"unique": "A user with that email already exists."}
    )

    address = models.TextField(null=True, blank=True)
    address_two = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    country_phone_number_code = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to=user_profile_picture_path, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            return super().save(*args, **kwargs)
        except IntegrityError as e:
            if "username" in str(e):
                raise IntegrityError(f"Username '{self.username}' is already taken.")
            elif "email" in str(e):
                raise IntegrityError(f"Email '{self.email}' is already taken.")
            raise

    def __str__(self):
        return self.username

    def is_customer(self):
        return self.groups.filter(name="Customers").exists()

    def is_seller(self):
        return self.groups.filter(name="Sellers").exists()

    def is_admin(self):
        return self.groups.filter(name="Admins").exists()
