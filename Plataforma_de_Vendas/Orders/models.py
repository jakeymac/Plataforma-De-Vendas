from django.db import models

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey('Accounts.CustomUser', on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=255)
    tracking_code = models.CharField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.created_at} - {self.total}'