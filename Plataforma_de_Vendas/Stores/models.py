from django.db import models

# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    url = models.CharField(max_length=75)

    def __str__(self):
        return self.name