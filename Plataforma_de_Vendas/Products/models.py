from core.models import UniqueIDModel
from django.db import IntegrityError, models


def product_image_upload_path(instance, filename):
    """
    Generate a dynamic path for image upload.
    Organize by product ID and image ID.
    """
    return f"product_images/{instance.product.id}/{instance.id}/{filename}"


class Product(UniqueIDModel):
    store = models.ForeignKey("Stores.Store", on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(
        "ProductSubcategory", on_delete=models.CASCADE, null=True, blank=True
    )
    product_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        error_messages={"unique": "Product with this name already exists"},
    )
    product_description = models.TextField(null=True, blank=True)
    properties = models.JSONField(null=True, blank=True, default=dict)
    is_active = models.BooleanField(default=True)
    draft = models.BooleanField(default=False)  # TODO implement this

    prices = models.JSONField(null=True, blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            return super().save(*args, **kwargs)
        except IntegrityError as e:
            if "product_name" in str(e):
                raise IntegrityError(f"Product name '{self.product_name}' already exists.")
            raise

    def __str__(self):
        return self.product_name

    class Meta:
        permissions = [
            ("edit_product", "Can edit product"),
            ("view_product_statistics", "Can view product statistics"),
        ]


class InitialProductState(UniqueIDModel):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    store = models.ForeignKey("Stores.Store", on_delete=models.CASCADE, null=True, blank=True)
    subcategory = models.ForeignKey(
        "ProductSubcategory", on_delete=models.CASCADE, null=True, blank=True
    )
    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_description = models.TextField(null=True, blank=True)
    properties = models.JSONField(null=True, blank=True, default=dict)
    is_active = models.BooleanField(default=True)
    draft = models.BooleanField(default=False)  # TODO implement this

    prices = models.JSONField(null=True, blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    original_created_at = models.DateTimeField()  # The original product's creation date

    def __str__(self):
        return f"Initial State of {self.product_name}"


class ProductImage(UniqueIDModel):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_upload_path, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    s3_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image and not self.s3_key:
            self.s3_key = self.image.name
            super().save(update_fields=["s3_key"])

    def __str__(self):
        return f"Image for {self.product.product_name} - {self.order}"


class InitialProductImage(models.Model):
    initial_product = models.ForeignKey("InitialProductState", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    s3_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    original_created_at = models.DateTimeField()  # The original product image's creation date
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Initial Image of {self.initial_product.product_name}"


class ProductInOrder(models.Model):
    order = models.ForeignKey("Orders.Order", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} - {self.quantity}"


class ProductCategory(UniqueIDModel):
    category_name = models.CharField(
        max_length=45,
        unique=True,
        error_messages={"unique": "Category with this name already exists"},
    )
    category_description = models.TextField(null=True, blank=True)
    top_subcategory_ids = (models.JSONField(default=list, null=True, blank=True),)
    top_subcategories_products = models.JSONField(
        null=True, blank=True
    )  # TODO update this or move it to a seperate model

    def __str__(self):
        return self.category_name


class ProductSubcategory(UniqueIDModel):
    category = models.ForeignKey("ProductCategory", on_delete=models.CASCADE)
    subcategory_name = models.CharField(
        max_length=45,
        unique=True,
        error_messages={"unique": "Subcategory with this name already exists"},
    )
    subcategory_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.subcategory_name


class ProductTopSubcategory(UniqueIDModel):
    subcategory = models.ForeignKey("ProductSubcategory", on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.subcategory} - {self.order}"

    class Meta:
        ordering = ["order"]  # Order by 'order' field
