from rest_framework import serializers
from .models import Product, ProductImage, ProductInOrder, ProductCategory, ProductSubCategory

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def validate(self, data):
        name = data.get('name')
        store_id = data.get('store_id')
        quantity = data.get('quantity')
        if quantity < 0:
            raise serializers.ValidationError({"quantity": "Quantity cannot be negative"})

        if Product.objects.filter(name=name, store_id=store_id).exists():
            raise serializers.ValidationError({"name": "Product with this name already exists in this store"})
            
        return data

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductInOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInOrder
        fields = '__all__'

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

    def validate(self, data):
        name = data.get('category_name')
        if ProductCategory.objects.filter(category_name=name).exists():
            raise serializers.ValidationError({"category_name": "Category with this name already exists"})
        if ProductSubCategory.objects.filter(subcategory_name=name).exists():
            raise serializers.ValidationError({"category_name": "Category with this name already exists as a subcategory"})
        return data

class ProductSubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), write_only=True)

    class Meta:
        model = ProductSubCategory
        fields = ['category', 'subcategory_name', 'subcategory_description']
        
    def validate(self, data):
        name = data.get('subcategory_name')
        if ProductCategory.objects.filter(category_name=name).exists():
            raise serializers.ValidationError({"subcategory_name": "Subcategory with this name already exists as a category"})
        if ProductSubCategory.objects.filter(subcategory_name=name).exists():
            raise serializers.ValidationError({"subcategory_name": "Subcategory with this name already exists"})
        return data