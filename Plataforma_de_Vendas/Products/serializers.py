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

    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        prices = instance.prices or {}
        data["prices"] = [
            {"price": float(value), "units": int(key)}
            for key, value in sorted(prices.items(), key=lambda item: int(item[0]))
        ]

        return data

    def to_internal_value(self, data):
        raw = data.copy()
        prices_list = raw.pop("prices", [])
        validated_data = super().to_internal_value(raw)
        validated_data["prices"] = self.validate_prices(prices_list)

        return validated_data

    def validate_prices(self, prices):

        if prices in (None, "", [], "null", "undefined"):
            return {}

        if not isinstance(prices, list):
            raise serializers.ValidationError(
                {"prices": "Prices must be a list of objects with price and units keys"}
            )

        seen_units = set()
        duplicate_units = set()
        seen_prices = set()
        duplicate_prices = set()
        result = []

        for item in prices:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    {"prices": "Each price must be an object with 'price' and 'units' keys"}
                )

            if "price" not in item or "units" not in item:
                raise serializers.ValidationError(
                    {"prices": "Each price object must contain 'price' and 'units' keys"}
                )

            try:
                price = float(item["price"])
            except (ValueError, TypeError):
                raise serializers.ValidationError({"prices": "Price must be a valid float"})

            try:
                units = int(item["units"])
            except (ValueError, TypeError):
                raise serializers.ValidationError({"prices": "Units must be a valid integer"})
            if units in seen_units:
                duplicate_units.add(units)
            else:
                seen_units.add(units)

            if price in seen_prices:
                duplicate_prices.add(price)
            else:
                seen_prices.add(price)

            result.append({"units": units, "price": price})

        if duplicate_units and duplicate_prices:
            raise serializers.ValidationError(
                {
                    "prices": (
                        f"Duplicate units found: {', '.join(map(str, duplicate_units))} and "
                        f"duplicate prices found: {', '.join(map(str, duplicate_prices))}"
                    )
                }
            )
        elif duplicate_units:
            raise serializers.ValidationError(
                {"prices": f"Duplicate units found: {', '.join(map(str, duplicate_units))}"}
            )
        elif duplicate_prices:
            raise serializers.ValidationError(
                {"prices": f"Duplicate prices found: {', '.join(map(str, duplicate_prices))}"}
            )

        return {
            int(item["price"]): int(item["units"]) for item in sorted(result, key=lambda x: x["units"])
        }


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
