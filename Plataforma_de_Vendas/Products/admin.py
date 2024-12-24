from django.contrib import admin
from .models import (Product, ProductImage, InitialProductImage, InitialProductState,
                    ProductInOrder, ProductCategory, ProductSubcategory, ProductTopSubcategory )

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(InitialProductState)
admin.site.register(InitialProductImage)
admin.site.register(ProductInOrder)
admin.site.register(ProductCategory)
admin.site.register(ProductSubcategory)
admin.site.register(ProductTopSubcategory)