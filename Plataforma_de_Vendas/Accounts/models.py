from django.db import models
from django.contrib.auth.models import AbstractUser
from nanoid import generate


def generate_unique_id():
    return generate(size=12)


class CustomUser(AbstractUser):

    def user_profile_picture_path(instance, filename):
        return f"profile_pictures/{instance.username}/{filename}"

    id = models.CharField(
        max_length=12,
        primary_key=True,
        default=generate_unique_id,
        editable=False,
        unique=True,
    )

    store = models.ForeignKey(
        "Stores.Store", on_delete=models.CASCADE, null=True, blank=True
    )  # For sellers to have a store
    stock_notifications = models.BooleanField(
        default=True, null=True, blank=True
    )  # For sellers to receive notifcations of their stock levels.

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    address = models.TextField(null=True, blank=True)
    address_two = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    country_phone_number_code = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path, null=True, blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)

    # Custom save method to generate unique id and ensure it is unique
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_unique_id()
        while True:
            try:
                super().save(*args, **kwargs)
                break
            # This error is caused by a non-unique id due to the 'unique=True' constraint on the id field
            except IntegrityError:
                # Regenerate the id and try again
                self.id = generate_unique_id()

    def __str__(self):
        return self.username

    def is_customer(self):
        return self.groups.filter(name="Customers").exists()

    def is_seller(self):
        return self.groups.filter(name="Sellers").exists()

    def is_admin(self):
        return self.groups.filter(name="Admins").exists()
