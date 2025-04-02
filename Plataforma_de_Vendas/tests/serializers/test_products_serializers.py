import pytest
from Products.models import Product
from Products.serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ProductSubcategorySerializer,
    ProductTopSubcategorySerializer,
)


@pytest.mark.django_db
class TestProductSerializer:
    """Test class for the Product serializer"""

    def test_to_representation_formats_prices_correctly(self):
        product = Product.objects.create(
            product_name="Test Product",
            prices={5: 10.0, 10: 20.5},  # Stored in DB as JSON with int keys
        )

        serializer = ProductSerializer(instance=product)
        data = serializer.data

        assert data["prices"] == {5: 10.0, 10: 20.5}
        assert isinstance(data["prices"], dict)
        assert all(isinstance(k, int) for k in data["prices"].keys())
        assert all(isinstance(v, float) for v in data["prices"].values())

    def test_valid_price_data(self, product_fixture):
        """Test valid price data"""
        product, _ = product_fixture

        data = {
            "product_name": product.product_name,
            "product_description": product.product_description,
            "properties": {"color": "red"},
            "prices": {1: 125},
        }

        serializer = ProductSerializer(instance=product, data=data)
        assert serializer.is_valid()
        assert serializer.validated_data["prices"] == {1: 125.0}

    def test_invalid_price_data(self, product_fixture):
        """Test invalid price data"""
        product, _ = product_fixture

        data = {
            "product_name": product.product_name,
            "product_description": product.product_description,
            "properties": {"color": "red"},
            "prices": {"none": 125},  # string price key
        }

        serializer = ProductSerializer(instance=product, data=data)
        assert not serializer.is_valid()
        assert (
            "Invalid format. Must be a dictionary with integer keys and float values."
            in serializer.errors["prices"][0]
        )

        data["prices"] = {1: "none"}  # string price value
        serializer = ProductSerializer(instance=product, data=data)
        assert not serializer.is_valid()
        assert (
            "Invalid format. Must be a dictionary with integer keys and float values."
            in serializer.errors["prices"][0]
        )

        data["prices"] = {1: None}  # None price value
        serializer = ProductSerializer(instance=product, data=data)
        assert not serializer.is_valid()
        assert (
            "Invalid format. Must be a dictionary with integer keys and float values."
            in serializer.errors["prices"][0]
        )

        data["prices"] = {None: 125}  # None price key
        serializer = ProductSerializer(instance=product, data=data)
        assert not serializer.is_valid()
        assert (
            "Invalid format. Must be a dictionary with integer keys and float values."
            in serializer.errors["prices"][0]
        )

        data["prices"] = [1, 125]  # list instead of dict
        serializer = ProductSerializer(instance=product, data=data)
        assert not serializer.is_valid()
        assert (
            "Prices must be a dictionary with integer keys and float values."
            in serializer.errors["prices"][0]
        )

    def test_updating_existing_product_with_existing_name(self, product_fixture):
        """Test updating an existing product with an existing name"""
        product, _ = product_fixture

        new_product = Product.objects.create(
            product_name="New Product Name",
            product_description="New description",
            properties={"color": "red"},
            prices={1: 125},
        )

        data = {
            "product_name": new_product.product_name,
            "product_description": "Updated description",
            "properties": {"color": "blue"},
            "prices": {1: 150},
        }

        serializer = ProductSerializer(instance=product, data=data)
        assert not serializer.is_valid()
        print("Testing...")
        print(serializer.errors)
        assert serializer.errors == {"product_name": ["Product with this name already exists"]}


@pytest.mark.django_db
class TestProductCategorySerializer:
    """Test class for the ProductCategory serializer"""

    def test_valid_data(self, category_fixture):
        """Test valid data"""
        data = {
            "category_name": category_fixture.category_name,
            "category_description": "New description",
        }

        serializer = ProductCategorySerializer(instance=category_fixture, data=data)
        assert serializer.is_valid()

    def test_invalid_data(self, subcategory_fixture):
        """Test invalid data"""
        data = {
            "category_name": subcategory_fixture.subcategory_name,
            "category_description": subcategory_fixture.subcategory_description,
        }

        serializer = ProductCategorySerializer(data=data)
        assert not serializer.is_valid()
        assert (
            "A subcategory with this name already exists as a subcategory"
            in serializer.errors["category_name"][0]
        )


@pytest.mark.django_db
class TestProductSubcategorySerializer:
    """Test class for the ProductSubcategory serializer"""

    def test_valid_data(self, subcategory_fixture):
        """Test valid data"""
        data = {
            "category_id": subcategory_fixture.category.id,
            "subcategory_name": subcategory_fixture.subcategory_name,
            "subcategory_description": "test description",
        }

        serializer = ProductSubcategorySerializer(instance=subcategory_fixture, data=data)
        assert serializer.is_valid()

    def test_invalid_data(self, category_fixture, subcategory_fixture):
        """Test invalid data"""
        data = {
            "category_id": category_fixture.id,
            "subcategory_name": category_fixture.category_name,
            "subcategory_description": "Test description",
        }

        serializer = ProductSubcategorySerializer(instance=subcategory_fixture, data=data)
        assert not serializer.is_valid()
        assert (
            "A category with this name already exists as a category"
            in serializer.errors["subcategory_name"][0]
        )


@pytest.mark.django_db
class TestProductTopSubcategorySerializer:
    """Test class for the ProductTopSubcategory serializer"""

    def test_valid_data(self, subcategory_fixture):
        """Test valid data"""
        data = {
            "subcategory": subcategory_fixture.id,
            "order": 1,
        }

        serializer = ProductTopSubcategorySerializer(data=data)
        assert serializer.is_valid()

    def test_invalid_data(self, subcategory_fixture):
        """Test invalid data"""
        data = {
            "subcategory": subcategory_fixture.id,
            "order": -1,
        }

        serializer = ProductTopSubcategorySerializer(data=data)
        assert not serializer.is_valid()
        assert "Order must be between 1 and 6" in serializer.errors["order"][0]

        data = {
            "subcategory": subcategory_fixture.id,
            "order": 7,
        }

        serializer = ProductTopSubcategorySerializer(data=data)
        assert not serializer.is_valid()
        assert "Order must be between 1 and 6" in serializer.errors["order"][0]
