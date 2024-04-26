from rest_framework import serializers
from .models import Product, ProductImage, ProductInOrder

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def run_validation(self, attrs):
        name = attrs.get('name')
        store_id = attrs.get('store_id')
        quantity = attrs.get('quantity')
        if quantity < 0:
            raise serializers.ValidationError({"quantity": "Quantity cannot be negative"})

        if Product.objects.filter(name=name, store_id=store_id).exists():
            raise serializers.ValidationError({"name": "Product with this name already exists in this store"})

        return attrs

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInOrder
        fields = '__all__'