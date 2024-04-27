from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # add additional fields in here
    ACCOUNT_TYPES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]

    account_type = models.CharField(choices=ACCOUNT_TYPES, max_length=10, default='customer')
    stock_notifications = models.BooleanField(default=True, null=True, blank=True) # For sellers to receive notifcations of their stock levels. 
    store = models.ForeignKey('Stores.Store', on_delete=models.CASCADE, null=True, blank=True) # For sellers to have a store

    address = models.TextField(null=True, blank=True)
    address_two = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

    def is_customer(self):
        return self.account_type == "customer"

    def is_seller(self):
        return self.account_type == "seller"

    def is_admin(self):
        return self.account_type == "admin"

    