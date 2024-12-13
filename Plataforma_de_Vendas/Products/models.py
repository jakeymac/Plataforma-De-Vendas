from django.db import models, IntegrityError
from nanoid import generate

def generate_unique_id():
    return generate(size=12)

class Product(models.Model):
    id = models.CharField(max_length=12, primary_key=True, default=generate_unique_id, editable=False, unique=True)
    store = models.ForeignKey('Stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.ForeignKey('ProductSubcategory', on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    properties = models.JSONField(null=True, blank=True, default=dict)
    is_active = models.BooleanField(default=True)
    draft = models.BooleanField(default=False) # TODO implement this

    created_on = models.DateTimeField(auto_now_add=True)

    # Custom save method to generate unique id and ensure it is unique
    def save(self, *args, **kwargs):
        if not self.id:
            self. id = generate_unique_id()
        while True:
            try:
                super().save(*args, **kwargs)
                break
            # This error is caused by a non-unique id due to the 'unique=True' constraint on the id field
            except IntegrityError:
                # Regenerate the id and try again
                self.id = generate_unique_id()
    
    def __str__(self):
        return self.product_name

class InitialProductState(models.Model):
    id = models.CharField(max_length=12, primary_key=True, default=generate_unique_id, editable=False, unique=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    store = models.ForeignKey('Stores.Store', on_delete=models.CASCADE, null=True, blank=True)
    sub_category = models.ForeignKey('ProductSubcategory', on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    properties = models.JSONField(null=True, blank=True, default=dict)
    is_active = models.BooleanField(default=True)
    draft = models.BooleanField(default=False) # TODO implement this

    # Custom save method to generate unique id and ensure it is unique
    def save(self, *args, **kwargs):
        if not self.id:
            self. id = generate_unique_id()
        while True:
            try:
                super().save(*args, **kwargs)
                break
            # This error is caused by a non-unique id due to the 'unique=True' constraint on the id field
            except IntegrityError:
                # Regenerate the id and try again
                self.id = generate_unique

    def __str__(self):
        return f"Initial State of {self.product_name}"

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.product.name

class InitialProductImage(models.Model):
    product = models.ForeignKey('InitialProductState', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return f"Initial Image of {self.product.name}"

class ProductInOrder(models.Model):
    order = models.ForeignKey('Orders.Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()   
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product} - {self.quantity}'

class ProductCategory(models.Model):
    id = models.CharField(max_length=12, primary_key=True, default=generate_unique_id, editable=False, unique=True)
    category_name = models.CharField(max_length=45)
    category_description = models.TextField(null=True, blank=True)
    top_subcategory_ids = models.JSONField(default=list, null=True, blank=True),
    top_subcategories_products = models.JSONField(null=True, blank=True) # TODO update this or move it to a seperate model

    # Custom save method to generate unique id and ensure it is unique
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_unique_id()
        while True:
            try:
                super().save(*args, **kwargs)
                break
            # This error is caused by a non-unique id due to the 'unique=True' constraint on the id field
            except IntegrityError:
                # Regenerate the id and try again
                self.id = generate_unique_id()

class ProductSubcategory(models.Model):
    id = models.CharField(max_length=12, primary_key=True, default=generate_unique_id, editable=False, unique=True)
    category = models.ForeignKey('ProductCategory', on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=45)
    subcategory_description = models.TextField(null=True, blank=True)

    # Custom save method to generate unique id and ensure it is unique
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_unique_id()
        while True:
            try:
                super().save(*args, **kwargs)
                break
            # This error is caused by a non-unique id due to the 'unique=True' constraint on the id field
            except IntegrityError:
                # Regenerate the id and try again
                self.id = generate_unique_id()


class ProductTopSubcategory(models.Model):
    id = models.CharField(max_length=12, primary_key=True, default=generate_unique_id, editable=False, unique=True)
    subcategory = models.ForeignKey('ProductSubcategory', on_delete=models.CASCADE)
    order = models.IntegerField()

    # Custom save method to generate unique id and ensure it is unique
    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_unique_id()
        while True:
            try:
                super().save(*args, **kwargs)
                break
            # This error is caused by a non-unique id due to the 'unique=True' constraint on the id field
            except IntegrityError:
                # Regenerate the id and try again
                self.id = generate_unique_id()

    class Meta:
        ordering = ['order']  # Order by 'order' field 