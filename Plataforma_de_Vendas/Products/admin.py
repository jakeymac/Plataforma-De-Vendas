from django.contrib import admin
from .models import Product, ProductImage, ProductInOrder, ProductCategory, ProductSubCategory

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductInOrder)
admin.site.register(ProductCategory)
admin.site.register(ProductSubCategory)