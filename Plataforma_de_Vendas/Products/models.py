from django.db import models

# Create your models here.
class Product(models.Model):
    store = models.ForeignKey('Stores.Store', on_delete=models.CASCADE)
    category = models.ForeignKey('ProductCategory', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    details = models.TextField(default='{}')
    minimum_quantity = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.product.name

class ProductInOrder(models.Model):
    order = models.ForeignKey('Orders.Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product} - {self.quantity}'


class ProductCategory(models.Model):
    category_name = models.CharField(max_length=45)
    