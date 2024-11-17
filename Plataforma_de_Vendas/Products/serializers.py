from rest_framework import serializers
from .models import Product, ProductImage, ProductInOrder, ProductCategory, ProductSubcategory, ProductTopSubcategory

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
        if ProductSubcategory.objects.filter(subcategory_name=name).exists():
            raise serializers.ValidationError({"category_name": "Category with this name already exists as a subcategory"})
        return data

class ProductSubcategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all(), write_only=True)

    class Meta:
        model = ProductSubcategory
        fields = ['category', 'subcategory_name', 'subcategory_description']
        
    def validate(self, data):
        name = data.get('subcategory_name')
        if ProductCategory.objects.filter(category_name=name).exists():
            raise serializers.ValidationError({"subcategory_name": "Subcategory with this name already exists as a category"})
        if ProductSubcategory.objects.filter(subcategory_name=name).exists():
            raise serializers.ValidationError({"subcategory_name": "Subcategory with this name already exists"})
        return data

class ProductTopSubcategorySerializer(serializers.ModelSerializer):
    class Meta:  
        model = ProductTopSubcategory
        fields = ['subcategory', 'order']

    
    def validate(self, data):
        order = data.get('order')
        if order < 1 or order > 6:
            raise serializers.ValidationError({"order": "Order must be between 1 and 6"})

        return data