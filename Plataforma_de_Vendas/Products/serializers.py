from rest_framework import serializers

from .models import (
    Product,
    ProductCategory,
    ProductImage,
    ProductInOrder,
    ProductSubcategory,
    ProductTopSubcategory,
)


class ProductSerializer(serializers.ModelSerializer):
    prices = serializers.JSONField()

    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "prices" in data and isinstance(data["prices"], dict):
            data["prices"] = {int(key): float(value) for key, value in data["prices"].items()}
        return data

    def validate_prices(self, prices):
        if not isinstance(prices, dict):
            raise serializers.ValidationError(
                "Prices must be a dictionary with integer keys and float values."
            )

        try:
            return {int(key): float(value) for key, value in prices.items()}
        except (ValueError, TypeError):
            raise serializers.ValidationError(
                "Invalid format. Must be a dictionary with integer keys and float values."
            )


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInOrder
        fields = "__all__"


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"

    def validate(self, data):
        name = data.get("category_name")
        if ProductSubcategory.objects.filter(subcategory_name=name).exists():
            raise serializers.ValidationError(
                {"category_name": ("A subcategory with this name already exists as a subcategory")}
            )
        return data


class ProductSubcategorySerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(), source="category"
    )

    class Meta:
        model = ProductSubcategory
        fields = ["category_id", "subcategory_name", "subcategory_description"]

    def validate(self, data):
        name = data.get("subcategory_name")

        if ProductCategory.objects.filter(category_name=name).exists():
            raise serializers.ValidationError(
                {"subcategory_name": ("A category with this name already exists as a category")}
            )
        return data


class ProductTopSubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTopSubcategory
        fields = ["subcategory", "order"]

    def validate(self, data):
        order = data.get("order")
        if order < 1 or order > 6:
            raise serializers.ValidationError({"order": "Order must be between 1 and 6"})

        return data
