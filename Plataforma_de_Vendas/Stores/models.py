from core.models import UniqueIDModel
from django.db import models


class Store(UniqueIDModel):
    store_name = models.CharField(
        max_length=255,
        unique=True,
        error_messages={
            "unique": "A store with this name already exists.",
        },
    )
    store_description = models.TextField()
    store_url = models.CharField(
        max_length=75,
        unique=True,
        error_messages={
            "unique": "A store with this URL already exists.",
        },
    )
    contact_email = models.EmailField(null=True, blank=True)
    store_logo = models.ImageField(upload_to="store_logos/", null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name
