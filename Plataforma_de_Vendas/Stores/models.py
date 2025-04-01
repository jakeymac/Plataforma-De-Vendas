from django.db import IntegrityError, models, transaction
from nanoid import generate

from core.models import UniqueIDModel


# Create your models here.
class Store(UniqueIDModel):
    store_name = models.CharField(max_length=255)
    store_description = models.TextField()
    store_url = models.CharField(max_length=75)
    contact_email = models.EmailField(null=True, blank=True)
    store_logo = models.ImageField(upload_to="store_logos/", null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name
