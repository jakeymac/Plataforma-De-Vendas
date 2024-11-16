from django.db import models

# Create your models here.
class Product(models.Model):
    store = models.ForeignKey('Stores.Store', on_delete=models.CASCADE)
    sub_category = models.ForeignKey('ProductSubcategory', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    details = models.TextField(default='{}')
    minimum_quantity = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)
    
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
    category_description = models.TextField(null=True, blank=True)
    top_subcategory_ids = models.JSONField(default=list, null=True, blank=True),
    top_subcategories_products = models.JSONField(null=True, blank=True) # TODO update this or move it to a seperate model

class ProductSubcategory(models.Model):
    category = models.ForeignKey('ProductCategory', on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=45)
    subcategory_description = models.TextField(null=True, blank=True)


class ProductTopSubcategory(models.Model):
    subcategory = models.ForeignKey('ProductSubcategory', on_delete=models.CASCADE)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']  # Order by 'order' field 