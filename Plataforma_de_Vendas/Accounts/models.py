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

    def __str__(self):
        return self.username

    def is_customer(self):
        return self.account_type == "customer"

    def is_seller(self):
        return self.account_type == "seller"

    def is_admin(self):
        return self.account_type == "admin"

    