import json

import pytest
from core.helpers import convert_prices_dict
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from Products.models import (
    InitialProductImage,
    InitialProductState,
    Product,
    ProductCategory,
    ProductImage,
    ProductSubcategory,
    ProductTopSubcategory,
)
from Stores.models import Store


@pytest.mark.django_db
class TestGetProductsByStoreEndpoint:
    """Test the get_products_by_store_endpoint - api/products/store/store_id -
    products-by-store-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "products-by-store-endpoint"

    def test_valid_access(self, store_fixture, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        url = reverse(self.view_name, kwargs={"store_id": store_fixture.id})

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data[0]["id"] == product.id
        assert response.data[0]["product_name"] == product.product_name
        assert response.data[0]["product_description"] == product.product_description
        assert response.data[0]["properties"] == product.properties
        assert response.data[0]["prices"] == product.prices

    def test_nonexistent_store(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"store_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Store not found with the id 0"


@pytest.mark.django_db
class TestGetProductsEndpoint:
    """Test the get_products_endpoint - api/products + api/products/product_id -
    all-products-endpoint + product-by-id-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.all_products_view_name = "all-products-endpoint"
        self.product_id_view_name = "product-by-id-endpoint"

    def test_existent_product(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        url = reverse(self.product_id_view_name, kwargs={"product_id": product.id})

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == product.id
        assert response.data["product_name"] == product.product_name
        assert response.data["product_description"] == product.product_description
        assert response.data["properties"] == product.properties
        assert response.data["prices"] == product.prices

    def test_nonexistent_product(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.product_id_view_name, kwargs={"product_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"

    def test_get_all_products(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        url = reverse(self.all_products_view_name)

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data["products"]
        assert len(response.data["products"]) == 1
        assert response.data["products"][0]["id"] == product.id
        assert response.data["products"][0]["product_name"] == product.product_name
        assert response.data["products"][0]["product_description"] == product.product_description
        assert response.data["products"][0]["properties"] == product.properties
        assert response.data["products"][0]["prices"] == product.prices


@pytest.mark.django_db
class TestRemoveProductEndpoint:
    """Test remove_product_endpoint - api/products/remove/product_id - remove-product-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "remove-product-endpoint"

    def test_admin_access(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, initial_product = product_fixture

        product_id = product.id
        initial_state_id = initial_product.id

        url = reverse(self.view_name, kwargs={"product_id": product_id})

        response = admin_client.delete(url)

        assert response.status_code == 204
        assert not Product.objects.filter(id=product_id).exists()
        assert not InitialProductState.objects.filter(id=initial_state_id).exists()
        assert not ProductImage.objects.filter(product=product).exists()
        assert not InitialProductImage.objects.filter(initial_product=initial_product).exists()

    def test_unauthorized_access(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        product_id = product.id

        url = reverse(self.view_name, kwargs={"product_id": product_id})

        response = customer_client.delete(url)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to delete this product"

    def test_nonexistent_product(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        url = reverse(self.view_name, kwargs={"product_id": "0"})

        response = admin_client.delete(url)

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"


@pytest.mark.django_db
class TestProductImagesEndpoint:
    """Test the product_images_endpoint -
    api/products/images/product_id - product-images-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "product-images-endpoint"

    def test_valid_access(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        url = reverse(self.view_name, kwargs={"product_id": product.id})
        response = customer_client.get(url)

        assert response.status_code == 200

        response_json = response.json()

        assert response_json["product_id"] == product.id
        assert response_json["images"][0]["id"] == product.productimage_set.first().id
        assert response_json["images"][0]["url"] == product.productimage_set.first().image.url

    def test_nonexistent_product(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"product_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"


@pytest.mark.django_db
class TestAddProductImageEndpoint:
    """Test the add_product_image_endpoint -
    api/products/add-image/product_id - add-product-image-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("add-product-image-endpoint")

    def test_valid_access(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"product_id": product.id, "image": image}

        response = admin_client.post(self.url, data)

        assert response.status_code == 201
        assert response.data["message"] == "Image added successfully"

        product_images = ProductImage.objects.filter(product=product)
        assert product_images.count() == 2  # The product already has an image, now this one
        assert product_images[1].order == 1

    def test_first_image_added(self, admin_fixture):
        """Test adding a first image to a product to test the order attribute."""
        admin_user, admin_client = admin_fixture

        product = Product.objects.create(
            product_name="Test Product Name",
            product_description="Test Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"product_id": product.id, "image": image}

        response = admin_client.post(self.url, data)

        assert response.status_code == 201
        assert response.data["message"] == "Image added successfully"

        product_images = ProductImage.objects.filter(product=product)
        assert product_images.count() == 1
        assert product_images[0].order == 0

    def test_image_with_order(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"product_id": product.id, "image": image, "order": 2}

        response = admin_client.post(self.url, data)

        assert response.status_code == 201
        assert response.data["message"] == "Image added successfully"

        product_images = ProductImage.objects.filter(product=product)
        assert product_images.count() == 2
        assert product_images[1].order == 2

    def test_invalid_order(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"product_id": product.id, "image": image, "order": "invalid"}

        response = admin_client.post(self.url, data)

        assert response.status_code == 400
        assert response.data["message"] == "Invalid order, must be an integer"

    def test_no_image(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        data = {"product_id": product.id}

        response = admin_client.post(self.url, data)

        assert response.status_code == 400
        assert response.data["message"] == "No image file provided"

    def test_unauthorized_access(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"product_id": product.id, "image": image}

        response = customer_client.post(self.url, data)

        assert response.status_code == 403
        assert (
            response.data["message"] == "You do not have permission to add an image to this product"
        )

    def test_nonexistent_product(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        data = {"product_id": "0", "image": image}

        response = admin_client.post(self.url, data)

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"


@pytest.mark.django_db
class TestRemoveProductImageEndpoint:
    """Test the remove_product_image_endpoint -
    api/products/remove_image/image_id - remove-product-image-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "remove-product-image-endpoint"

    def test_valid_access(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        image = ProductImage.objects.filter(product=product)[0]

        url = reverse(self.view_name, kwargs={"image_id": image.id})

        response = admin_client.delete(url)

        assert response.status_code == 204
        assert not ProductImage.objects.filter(id=image.id).exists()

    def test_unauthorized_access(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        image = ProductImage.objects.filter(product=product)[0]

        url = reverse(self.view_name, kwargs={"image_id": image.id})

        response = customer_client.delete(url)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to remove this image"

    def test_nonexistent_image(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        url = reverse(self.view_name, kwargs={"image_id": "0"})

        response = admin_client.delete(url)

        assert response.status_code == 404
        assert response.data["message"] == "Image not found with the id 0"


@pytest.mark.django_db
class TestProductsInOrderEndpoint:
    """Test the products_in_order_endpoint -
    api/products/order/order_id - products-in-order-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "products-in-order-endpoint"

    def test_valid_access(self, customer_fixture, product_fixture, order_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture
        order = order_fixture

        url = reverse(self.view_name, kwargs={"order_id": order.id})

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data[0]["product"] == product.id

    def test_nonexistent_order(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"order_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Order not found with the id 0"


@pytest.mark.django_db
class TestFindProductsInCategoryEndpoint:
    """Test the find_products_in_category_endpoint -
    api/products/category/category_id - find-products-in-category-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "find-products-in-category-endpoint"

    def test_valid_access(self, customer_fixture, product_fixture, category_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture
        category = category_fixture

        url = reverse(self.view_name, kwargs={"category_id": category.id})

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data[0]["id"] == product.id

    def test_nonexistent_category(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"category_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Category not found with the id 0"


@pytest.mark.django_db
class TestGetSubcategoriesEndpoint:
    """Test the get_subcategories_endpoint -
    api/products/subcategories - subcategories-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("all-subcategories-endpoint")

    def test_valid_access(self, customer_fixture, subcategory_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture

        response = customer_client.get(self.url)

        assert response.status_code == 200
        assert response.data[0]["subcategory_name"] == subcategory.subcategory_name
        assert response.data[0]["subcategory_description"] == subcategory.subcategory_description

    def test_no_subcategories_found(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        response = customer_client.get(self.url)

        assert response.status_code == 404
        assert response.data["message"] == "No subcategories found"


@pytest.mark.django_db
class TestGetSubcategoryEndpoint:
    """Test the get_subcategory_endpoint -
    api/products/subcategory/subcategory_id - subcategory-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "subcategory-endpoint"

    def test_valid_access(self, customer_fixture, subcategory_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture

        url = reverse(self.view_name, kwargs={"subcategory_id": subcategory.id})

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data["subcategory_name"] == subcategory.subcategory_name

    def test_nonexistent_subcategory(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"subcategory_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Subcategory not found with the id 0"


@pytest.mark.django_db
class TestGetSubcategoriesByCategoryEndpoint:
    """Test the get_subcategories_by_category_endpoint -
    api/products/subcategories/category_id - subcategories-by-category-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "subcategories-by-category-endpoint"

    def test_valid_access(self, customer_fixture, subcategory_fixture, category_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture
        category = category_fixture

        url = reverse(self.view_name, kwargs={"category_id": category.id})

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data[0]["subcategory_name"] == subcategory.subcategory_name

    def test_nonexistent_category(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"category_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Category not found with the id 0"


@pytest.mark.django_db
class TestGetCategoriesEndpoint:
    """Test the get_categories_endpoint - api/products/categories - categories-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("all-categories-endpoint")

    def test_valid_access(self, customer_fixture, category_fixture):
        customer_user, customer_client = customer_fixture
        category = category_fixture

        response = customer_client.get(self.url)

        assert response.status_code == 200
        assert response.data[0]["category_name"] == category.category_name

    def test_no_categories_found(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        response = customer_client.get(self.url)

        assert response.status_code == 404
        assert response.data["message"] == "No categories found"


@pytest.mark.django_db
class TestGetCategoryEndpoint:
    """Test the get_category_endpoint - api/products/category/category_id - category-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "category-endpoint"

    def test_valid_access(self, customer_fixture, category_fixture):
        customer_user, customer_client = customer_fixture
        category = category_fixture

        url = reverse(self.view_name, kwargs={"category_id": category.id})

        response = customer_client.get(url)

        assert response.status_code == 200
        assert response.data["category_name"] == category.category_name

    def test_nonexistent_category(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"category_id": "0"})

        response = customer_client.get(url)

        assert response.status_code == 404
        assert response.data["message"] == "Category not found with the id 0"


@pytest.mark.django_db
class TestAddSubcategoryEndpoint:
    """Test the add_subcategory_endpoint -
    api/products/add-subcategory/category_id - add-subcategory-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("add-subcategory-endpoint")

    def test_valid_access(self, admin_fixture, category_fixture):
        admin_user, admin_client = admin_fixture
        category = category_fixture

        data = {
            "category_id": category.id,
            "subcategory_name": "Test Subcategory Name",
            "subcategory_description": "Test Subcategory Description",
        }

        response = admin_client.post(self.url, data)

        assert response.status_code == 201
        assert response.data["message"] == "Subcategory added successfully"

        subcategories = ProductSubcategory.objects.filter(category=category)
        assert subcategories.count() == 1
        assert subcategories[0].subcategory_name == "Test Subcategory Name"
        assert subcategories[0].subcategory_description == "Test Subcategory Description"

    def test_unauthorized_access(self, customer_fixture, category_fixture):
        customer_user, customer_client = customer_fixture
        category = category_fixture

        data = {
            "category_id": category.id,
            "subcategory_name": "Test Subcategory Name",
            "subcategory_description": "Test Subcategory Description",
        }

        response = customer_client.post(self.url, data)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to add a subcategory"

    def test_existing_subcategory(self, subcategory_fixture, admin_fixture):
        subcategory = subcategory_fixture
        admin_user, admin_client = admin_fixture

        data = {
            "category_id": subcategory.category.id,
            "subcategory_name": subcategory.subcategory_name,
            "subcategory_description": subcategory.subcategory_description,
        }

        response = admin_client.post(self.url, data)

        assert response.status_code == 400
        assert response.data["subcategory_name"][0] == "Subcategory with this name already exists"

    def test_nonexistent_category(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {
            "category_id": "0",
            "subcategory_name": "Test Subcategory Name",
            "subcategory_description": "Test Subcategory Description",
        }

        response = admin_client.post(self.url, data)

        assert response.status_code == 404
        assert response.data["message"] == "Category not found with the id 0"


@pytest.mark.django_db
class TestAddCategoryEndpoint:
    """Test the add_category_endpoint - api/products/add-category - add-category-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("add-category-endpoint")

    def test_valid_access(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {
            "category_name": "Test Category Name",
            "category_description": "Test Category Description",
        }

        response = admin_client.post(self.url, data)

        assert response.status_code == 201
        assert response.data["message"] == "Category added successfully"

        categories = ProductCategory.objects.all()
        assert categories.count() == 1
        assert categories[0].category_name == "Test Category Name"

    def test_unauthorized_access(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        data = {
            "category_name": "Test Category Name",
            "category_description": "Test Category Description",
        }

        response = customer_client.post(self.url, data)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to add a category"

    def test_existent_category_name(self, admin_fixture, category_fixture):
        admin_user, admin_client = admin_fixture
        category = category_fixture

        data = {
            "category_name": category.category_name,
            "category_description": "Test Category Description",
        }

        response = admin_client.post(self.url, data)

        assert response.status_code == 400
        assert response.data["category_name"][0] == "Category with this name already exists"


@pytest.mark.django_db
class TestUpdateCategoryEndpoint:
    """Test the update_category_endpoint -
    api/products/categories/update/ - update-category-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("update-category-endpoint")

    def test_valid_access(self, admin_fixture, category_fixture):
        admin_user, admin_client = admin_fixture
        category = category_fixture

        data = {
            "category_id": category.id,
            "category_name": "New Test Category Name",
            "category_description": "New test category description",
        }

        response = admin_client.put(self.url, data)
        assert response.status_code == 200
        assert response.data["message"] == "Category updated successfully"

        category = ProductCategory.objects.get(id=category.id)
        assert category.category_name == "New Test Category Name"
        assert category.category_description == "New test category description"

    def test_existing_category_name(self, admin_fixture, category_fixture):
        admin_user, admin_client = admin_fixture
        category = category_fixture

        new_category = ProductCategory.objects.create(
            category_name="New Category Name", category_description="New Category Description"
        )

        data = {
            "category_id": new_category.id,
            "category_name": category.category_name,
            "category_description": "Test Category Description",
        }

        response = admin_client.put(self.url, data)

        assert response.status_code == 400
        assert response.data["category_name"][0] == "Category with this name already exists"

    def test_non_existent_category(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {
            "category_id": "0",
            "category_name": "Testing category name",
            "category_description": "Testing category description",
        }

        response = admin_client.put(self.url, data)

        assert response.status_code == 404
        assert response.data["message"] == "Category not found with the id 0"

    def test_unauthenticated_access(self, customer_fixture, category_fixture):
        customer_user, customer_client = customer_fixture
        category = category_fixture

        data = {
            "category_id": category.id,
            "category_name": "Updated category name",
            "category_description": "Updated description",
        }

        response = customer_client.put(self.url, data)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to update this category"


@pytest.mark.django_db
class TestUpdateSubcategoryEndpoint:
    """Test the update_subcategory_endpoint -
    api/products/subcategories/update/ - update-subcategory-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("update-subcategory-endpoint")

    def test_valid_access(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        data = {
            "subcategory_id": subcategory.id,
            "subcategory_name": "New Test Subcategory Name",
            "subcategory_description": "New test subcategory description",
        }

        response = admin_client.put(self.url, data)

        assert response.status_code == 200
        assert response.data["message"] == "Subcategory updated successfully"

        subcategory = ProductSubcategory.objects.get(id=subcategory.id)
        assert subcategory.subcategory_name == "New Test Subcategory Name"
        assert subcategory.subcategory_description == "New test subcategory description"

    def test_existing_subcategory_name(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        new_subcategory = ProductSubcategory.objects.create(
            category=subcategory.category,
            subcategory_name="New Subcategory Name",
            subcategory_description="New Subcategory Description",
        )

        data = {
            "subcategory_id": new_subcategory.id,
            "subcategory_name": subcategory.subcategory_name,
            "subcategory_description": "Test Subcategory Description",
        }

        response = admin_client.put(self.url, data)

        assert response.status_code == 400
        assert response.data["subcategory_name"][0] == "Subcategory with this name already exists"

    def test_non_existent_subcategory(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {
            "subcategory_id": "0",
            "subcategory_name": "Testing subcategory name",
            "subcategory_description": "Testing subcategory description",
        }

        response = admin_client.put(self.url, data)

        assert response.status_code == 404
        assert response.data["message"] == "Subcategory not found with the id 0"

    def test_unauthenticated_access(self, customer_fixture, subcategory_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture

        data = {
            "subcategory_id": subcategory.id,
            "subcategory_name": "Updated subcategory name",
            "subcategory_description": "Updated description",
        }

        response = customer_client.put(self.url, data)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to update this subcategory"


@pytest.mark.django_db
class TestRemoveCategoryEndpoint:
    """Test the remove_category_endpoint -
    api/products/categories/remove/category_id/ - remove-category-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "remove-category-endpoint"

    def test_valid_access(self, admin_fixture, category_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        category = category_fixture
        subcategory = subcategory_fixture

        url = reverse(self.view_name, kwargs={"category_id": category.id})

        response = admin_client.delete(url)

        assert response.status_code == 204
        assert response.data["message"] == "Category removed successfully"
        assert not ProductCategory.objects.filter(id=category.id).exists()

        # Confirm any product subcategories belonging to this category get deleted
        assert not ProductSubcategory.objects.filter(id=subcategory.id).exists()

        assert response.status_code == 204
        assert response.data["message"] == "Category removed successfully"
        assert not ProductCategory.objects.filter(id=category.id).exists()

    def test_nonexistent_category(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        url = reverse(self.view_name, kwargs={"category_id": "0"})

        response = admin_client.delete(url)

        assert response.status_code == 404
        assert response.data["category"] == "Category not found with the id 0"

    def test_unauthorized_access(self, customer_fixture, category_fixture):
        customer_user, customer_client = customer_fixture
        category = category_fixture

        url = reverse(self.view_name, kwargs={"category_id": category.id})

        response = customer_client.delete(url)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to remove this category"


@pytest.mark.django_db
class TestRemoveSubcategoryEndpoint:
    """Test the remove_subcategory_endpoint -
    api/products/subcategories/remove/subcategory_id/ - remove-subcategory-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "remove-subcategory-endpoint"

    def test_valid_access(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        url = reverse(self.view_name, kwargs={"subcategory_id": subcategory.id})

        response = admin_client.delete(url)

        assert response.status_code == 204
        assert response.data["message"] == "Subcategory removed successfully"
        assert not ProductSubcategory.objects.filter(id=subcategory.id).exists()

    def test_nonexistent_subcategory(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        url = reverse(self.view_name, kwargs={"subcategory_id": "0"})

        response = admin_client.delete(url)

        assert response.status_code == 404
        assert response.data["message"] == "Subcategory not found with the id 0"

    def test_unauthorized_access(self, customer_fixture, subcategory_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture

        url = reverse(self.view_name, kwargs={"subcategory_id": subcategory.id})

        response = customer_client.delete(url)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to remove this subcategory"


@pytest.mark.django_db
class TestGetTopSubcategoriesEndpoint:
    """Test the get_top_subcategories_endpoint -
    api/products/top-subcategories - top-subcategories-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("top-subcategories-endpoint")

    def test_valid_access(self, customer_fixture, subcategory_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture

        top_category = ProductTopSubcategory.objects.get(subcategory=subcategory)

        response = customer_client.get(self.url)

        assert response.status_code == 200
        assert response.data[top_category.order]["id"] == subcategory.id
        assert response.data[top_category.order]["subcategory_name"] == subcategory.subcategory_name
        assert (
            response.data[top_category.order]["subcategory_description"]
            == subcategory.subcategory_description
        )


@pytest.mark.django_db
class TestUpdateTopSubcategoriesEndpoint:
    """Test the update_top_subcategories_endpoint -
    api/products/update-top-subcategories - update-top-subcategories-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("update-top-subcategories-endpoint")

    def create_subcategories(self, subcategory_fixture, count=6):
        """Generates data to use in testing"""
        subcategory = subcategory_fixture

        subcategory_names = [f"New Subcategory {i+1}" for i in range(count)]
        subcategory_descriptions = [f"New Subcategory {i+1} Description" for i in range(count)]

        new_subcategory_ids = []
        for i in range(count):
            new_subcategory = ProductSubcategory.objects.create(
                category=subcategory.category,
                subcategory_name=subcategory_names[i],
                subcategory_description=subcategory_descriptions[i],
            )
            new_subcategory_ids.append(new_subcategory.id)

        return {subcategory_names[i]: new_subcategory_ids[i] for i in range(count)}

    def test_valid_access(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        data = self.create_subcategories(subcategory, 6)

        response = admin_client.put(self.url, data)

        assert response.status_code == 200
        assert response.data["message"] == "Top subcategories updated successfully"

        # Ensure original top subcategory was deleted
        assert not ProductTopSubcategory.objects.filter(subcategory=subcategory).exists()

        assert ProductTopSubcategory.objects.count() == 6

        for i in range(6):
            top_subcategory = ProductTopSubcategory.objects.get(order=i + 1)
            assert top_subcategory.subcategory.subcategory_name == list(data.keys())[i]

    def test_not_enough_subcategories(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        data = self.create_subcategories(subcategory, 5)
        response = admin_client.put(self.url, data)

        assert response.status_code == 400
        assert response.data["message"] == "There must be 6 top subcategories"

    def test_unauthenticated_access(self, customer_fixture, subcategory_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture

        data = self.create_subcategories(subcategory, 6)

        response = customer_client.put(self.url, data)

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to update top subcategories"

    def test_duplicate_subcategories(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        data = self.create_subcategories(subcategory, 6)
        data["New Subcategory 1"] = data["New Subcategory 2"]

        response = admin_client.put(self.url, data)

        assert response.status_code == 400
        assert response.data["message"] == "Duplicate subcategories found"

        assert data["New Subcategory 1"] in response.data["duplicates"]
        assert data["New Subcategory 2"] in response.data["duplicates"]

    def test_nonexistent_subcategory_ids(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        data = self.create_subcategories(subcategory, 6)
        data["New Subcategory 1"] = "non_existent_id"
        data["New Subcategory 2"] = "non_existent_id_2"

        response = admin_client.put(self.url, data)

        assert response.status_code == 404
        assert (
            response.data["message"]
            == "Subcategories not found with id(s): ['non_existent_id', 'non_existent_id_2']"
        )


@pytest.mark.django_db
class TestAddProductEndpoint:
    """Test the add_product_endpoint - api/products/add-product - add-product-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("add-product-endpoint")

    def test_valid_access(self, admin_fixture, subcategory_fixture):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture

        data = {
            "product_name": "Test Product Name",
            "product_description": "Test Product Description",
            "properties": {"color": "red", "size": "small"},
            "prices": {5: 10.0, 10: 5.0},
            "subcategory": subcategory.id,
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 201
        assert response.data["message"] == "Product added successfully"

        product = Product.objects.get(product_name="Test Product Name")
        assert product.product_description == "Test Product Description"
        assert product.properties == {"color": "red", "size": "small"}
        assert convert_prices_dict(product.prices) == {5: 10.0, 10: 5.0}
        assert product.subcategory_id == subcategory.id

    def test_already_existing_product_name(
        self, admin_fixture, subcategory_fixture, product_fixture
    ):
        admin_user, admin_client = admin_fixture
        subcategory = subcategory_fixture
        product, _ = product_fixture

        data = {
            "product_name": product.product_name,
            "product_description": "Test Product Description",
            "properties": {"color": "red", "size": "small"},
            "prices": {5: 10.0, 10: 5.0},
            "subcategory": subcategory.id,
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 400
        assert response.data["message"] == "Product with that name already exists"

    def test_unauthenticated_access(self, customer_fixture, subcategory_fixture):
        customer_user, customer_client = customer_fixture
        subcategory = subcategory_fixture

        data = {
            "product_name": "Test Product Name",
            "product_description": "Test Product Description",
            "properties": {"color": "red", "size": "small"},
            "prices": {5: 10.0, 10: 5.0},
            "subcategory": subcategory.id,
        }

        response = customer_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to add a product"


@pytest.mark.django_db
class TestRollbackProductChangesEndpoint:
    """Test the rollback_product_changes_endpoint -
    api/products/rollback/product_id - rollback-product-changes-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("rollback-product-changes-endpoint")

    def test_valid_access(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        product = Product.objects.create(
            product_name="Rollback Product Name",
            product_description="Rollback Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        image = SimpleUploadedFile(
            "rollback_test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        product_image = ProductImage.objects.create(product=product, image=image)

        initial_values = {
            "product_name": "Initial Rollback Product Name",
            "product_description": "Initial Rollback Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "original_created_at": product.created_at,
        }

        initial_state = InitialProductState.objects.create(
            product=product,
            product_name=initial_values["product_name"],
            product_description=initial_values["product_description"],
            properties=initial_values["properties"],
            prices=initial_values["prices"],
            original_created_at=initial_values["original_created_at"],
        )

        initial_image = SimpleUploadedFile(
            "rollback_test_initial_image.jpg", b"file_content", content_type="image/jpeg"
        )
        initial_product_image = InitialProductImage.objects.create(
            initial_product=initial_state,
            image=initial_image,
            original_created_at=product_image.created_at,
        )

        data = {"product_id": product.id, "initial_product_state_id": initial_state.id}

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 200
        assert response.data["message"] == "Product rolled back successfully"

        # Retreive any changes made to the product
        product.refresh_from_db()

        assert product.product_name == initial_values["product_name"]
        assert product.product_description == initial_values["product_description"]
        assert product.properties == initial_values["properties"]
        assert convert_prices_dict(product.prices) == initial_values["prices"]

        assert not ProductImage.objects.filter(id=product_image.id).exists()
        assert not InitialProductImage.objects.filter(id=initial_product_image.id).exists()

        assert ProductImage.objects.filter(image=initial_product_image.image).exists()

    def test_nonexistent_product(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        _, initial_product = product_fixture

        data = {"product_id": "0", "initial_product_state_id": initial_product.id}

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"

    def test_non_existent_initial_product(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        data = {"product_id": product.id, "initial_product_state_id": "0"}

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Initial product state not found with the id 0"

    def test_non_existent_product_and_initial_product(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture

        data = {"product_id": "0", "initial_product_state_id": "1"}

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert (
            response.data["message"]
            == "Product with id 0 and initial product state with id 1 not found"
        )

    def test_unauthorized_to_change_product(self, seller_fixture):
        seller_user, seller_client = seller_fixture

        store = Store.objects.create(store_name="New Test Store")

        product = Product.objects.create(
            product_name="Rollback Product Name",
            product_description="Rollback Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
            store=store,
        )

        initial_values = {
            "product_name": "Initial Rollback Product Name",
            "product_description": "Initial Rollback Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "original_created_at": product.created_at,
        }

        initial_state = InitialProductState.objects.create(
            product=product,
            product_name=initial_values["product_name"],
            product_description=initial_values["product_description"],
            properties=initial_values["properties"],
            prices=initial_values["prices"],
            original_created_at=initial_values["original_created_at"],
        )

        data = {"product_id": product.id, "initial_product_state_id": initial_state.id}

        response = seller_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to rollback this product"

    def test_unauthorized_to_change_all_products(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, initial_product = product_fixture

        data = {"product_id": product.id, "initial_product_state_id": initial_product.id}

        response = customer_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to rollback products"


@pytest.mark.django_db
class TestCreateInitialProductStateEndpoint:
    """Test the create_initial_product_state_endpoint -
    api/products/create_initial_product_state/ - create-initial-product-state-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("create-initial-product-state-endpoint")

    def test_valid_access(self, admin_fixture, store_fixture):
        admin_user, admin_client = admin_fixture
        store = store_fixture

        new_product = Product.objects.create(
            product_name="Initial Product Name",
            product_description="Initial Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
            store=store,
        )

        new_product_image_file = SimpleUploadedFile(
            "new_product_image.jpg", b"file_content", content_type="image/jpeg"
        )
        new_product_image = ProductImage.objects.create(
            product=new_product, image=new_product_image_file
        )

        data = {"product_id": new_product.id}

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 201
        assert response.data["message"] == "Initial product state created successfully"

        assert InitialProductState.objects.filter(product=new_product).exists()

        initial_state = InitialProductState.objects.get(product=new_product)

        assert InitialProductImage.objects.filter(initial_product=initial_state).exists()

        initial_image = InitialProductImage.objects.get(initial_product=initial_state)

        assert initial_state.product_name == new_product.product_name
        assert initial_state.product_description == new_product.product_description
        assert initial_state.properties == new_product.properties
        assert convert_prices_dict(initial_state.prices) == new_product.prices
        assert initial_state.original_created_at == new_product.created_at

        assert initial_image.image == new_product_image.image
        assert initial_image.original_created_at == new_product_image.created_at

    def test_unauthorized_on_product(self, seller_fixture):
        seller_user, seller_client = seller_fixture

        new_store = Store.objects.create(store_name="Initial Product Test Store")

        new_product = Product.objects.create(
            product_name="Initial Product Name",
            product_description="Initial Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
            store=new_store,
        )

        data = {"product_id": new_product.id}

        response = seller_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert (
            response.data["message"]
            == "You do not have permission to create an initial product state for this product"
        )

    def test_nonexistend_product(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {"product_id": "0"}

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"

    def test_unauthorized_on_all_products(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        data = {"product_id": product.id}

        response = customer_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert (
            response.data["message"]
            == "You do not have permission to create initial product states"
        )


@pytest.mark.django_db
class TestAutosaveProductEndpoint:
    """Test the autosave_product_endpoint -
    api/products/autosave_product/ - autosave-product-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("autosave-product-endpoint")

    def test_valid_access(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        new_product = Product.objects.create(
            product_name="Autosave Product Name",
            product_description="Autosave Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        image_file = SimpleUploadedFile(
            "autosave_test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        image_file_2 = SimpleUploadedFile(
            "autosave_test_image_2.jpg", b"file_content", content_type="image/jpeg"
        )

        product_image = ProductImage.objects.create(product=new_product, image=image_file)
        product_image_2 = ProductImage.objects.create(product=new_product, image=image_file_2)

        data = {
            "product_id": new_product.id,
            "product_name": "Autosave Product Name",
            "product_description": "Autosave Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": [product_image.id, product_image_2.id],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 200
        assert response.data["message"] == "Product autosaved successfully"

        new_product.refresh_from_db()

        assert new_product.product_name == "Autosave Product Name"
        assert new_product.product_description == "Autosave Product Description"
        assert new_product.properties == {"color": "blue", "size": "large"}
        assert convert_prices_dict(new_product.prices) == {5: 20.0, 10: 10.0}

        assert ProductImage.objects.filter(product=new_product).count() == 2

        assert ProductImage.objects.get(id=product_image.id).order == 0
        assert ProductImage.objects.get(id=product_image_2.id).order == 1

    def test_unauthorized_on_product(self, seller_fixture):
        seller_user, seller_client = seller_fixture

        new_store = Store.objects.create(store_name="Autosave Product Test Store")

        new_product = Product.objects.create(
            product_name="Autosave Product Name",
            product_description="Autosave Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
            store=new_store,
        )

        new_image = SimpleUploadedFile(
            "autosave_test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        product_image = ProductImage.objects.create(product=new_product, image=new_image)

        data = {
            "product_id": new_product.id,
            "product_name": "Autosave Product Name",
            "product_description": "Autosave Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": [product_image.id],
        }

        response = seller_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to autosave this product"

    def test_repeated_product_name(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        new_product = Product.objects.create(
            product_name="Autosave Product Name",
            product_description="Autosave Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        image_file = SimpleUploadedFile(
            "autosave_test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        product_image = ProductImage.objects.create(product=new_product, image=image_file)

        data = {
            "product_id": new_product.id,
            "product_name": product.product_name,
            "product_description": "Autosave Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": [product_image.id],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 400
        assert response.data["product_name"][0] == "Product with this name already exists"

    def test_nonexistent_image_ids(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        new_product = Product.objects.create(
            product_name="Autosave Product Name",
            product_description="Autosave Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        data = {
            "product_id": new_product.id,
            "product_name": "Autosave Product Name",
            "product_description": "Autosave Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": ["0", "1"],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Images not found with the ids ['0', '1']"

    def test_nonexistent_product(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {
            "product_id": "0",
            "product_name": "Autosave Product Name",
            "product_description": "Autosave Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": ["0"],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"

    def test_unauthorized_on_all_products(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        data = {
            "product_id": product.id,
            "product_name": "Autosave Product Name",
            "product_description": "Autosave Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": ["0"],
        }

        response = customer_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to autosave products"


@pytest.mark.django_db
class TestFinalSaveProductEndpoint:
    """Test the final_save_product_endpoint -
    api/products/final_save_product/ - final-save-product-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("final-save-product-endpoint")

    def test_valid_access(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, inital_state = product_fixture

        product_image = ProductImage.objects.get(product=product)

        data = {
            "product_id": product.id,
            "product_name": "Final Save Product Name",
            "product_description": "Final Save Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": [product_image.id],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 200
        assert response.data["message"] == "Product saved successfully"

        product.refresh_from_db()

        assert product.product_name == "Final Save Product Name"
        assert product.product_description == "Final Save Product Description"
        assert product.properties == {"color": "blue", "size": "large"}
        assert convert_prices_dict(product.prices) == {5: 20.0, 10: 10.0}

        assert ProductImage.objects.filter(product=product).count() == 1

        assert not InitialProductImage.objects.filter(initial_product=inital_state).exists()
        assert not InitialProductState.objects.filter(product=product).exists()

    def test_unauthorized_on_product(self, seller_fixture):
        seller_user, seller_client = seller_fixture

        new_store = Store.objects.create(store_name="Final Save Product Test Store")

        new_product = Product.objects.create(
            product_name="Final Save Product Name",
            product_description="Final Save Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
            store=new_store,
        )

        new_image = SimpleUploadedFile(
            "final_save_test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        product_image = ProductImage.objects.create(product=new_product, image=new_image)

        data = {
            "product_id": new_product.id,
            "product_name": "Final Save Product Name",
            "product_description": "Final Save Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": [product_image.id],
        }

        response = seller_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to save this product"

    def test_repeated_product_name(self, admin_fixture, product_fixture):
        admin_user, admin_client = admin_fixture
        product, _ = product_fixture

        new_product = Product.objects.create(
            product_name="Final Save Product Name",
            product_description="Final Save Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        image_file = SimpleUploadedFile(
            "final_save_test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        product_image = ProductImage.objects.create(product=new_product, image=image_file)

        data = {
            "product_id": new_product.id,
            "product_name": product.product_name,
            "product_description": "Final Save Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": [product_image.id],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 400
        assert response.data["product_name"][0] == "Product with this name already exists"

    def test_nonexistent_image_ids(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        new_product = Product.objects.create(
            product_name="Final Save Product Name",
            product_description="Final Save Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        data = {
            "product_id": new_product.id,
            "product_name": "Final Save Product Name",
            "product_description": "Final Save Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": ["0", "1"],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Images not found with the ids ['0', '1']"

    def test_nonexistent_product(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {
            "product_id": "0",
            "product_name": "Final Save Product Name",
            "product_description": "Final Save Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": ["0"],
        }

        response = admin_client.post(self.url, data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Product not found with the id 0"

    def test_unauthorized_on_all_products(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        data = {
            "product_id": product.id,
            "product_name": "Final Save Product Name",
            "product_description": "Final Save Product Description",
            "properties": {"color": "blue", "size": "large"},
            "prices": {5: 20.0, 10: 10.0},
            "image_ids": ["0"],
        }

        response = customer_client.post(self.url, data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You do not have permission to save products"


@pytest.mark.django_db
class TestProductSearchEndpoint:
    """Test the product_search_endpoint -
    api/products/product_id/ - search-products-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("search-products-endpoint")

    def test_invalid_filter_format(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture

        data = {"search": "", "sort": "price-asc", "filters": ["nonexistent_filter"]}

        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 400
        assert response.data["message"] == "Invalid filters format"

    def test_invalid_sort(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture

        data = {"search": "", "sort": "invalid_sort", "filters": {}}

        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 400
        assert response.data["message"] == "Invalid sort parameter: invalid_sort"

    def test_invalid_filter(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture

        data = {
            "search": "",
            "sort": "price-asc",
            "filters": json.dumps({"nonexistent_filter": ["value"], "another_filter": ["value"]}),
        }

        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 400
        assert (
            response.data["message"]
            == "Invalid filter parameter(s): nonexistent_filter, another_filter"
        )

    def test_search_product_name(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        data = {"search": product.product_name, "sort": "price-asc", "filters": {}}

        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 200
        assert len(response.data["products"]) == 1
        assert response.data["products"][0]["product_name"] == product.product_name

    def test_nonexistent_product(self, customer_fixture):
        customer_user, customer_client = customer_fixture

        data = {"search": "Nonexistent Product", "sort": "price-asc", "filters": {}}

        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 200
        assert len(response.data["products"]) == 0

    def test_valid_filter(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        new_category = ProductCategory.objects.create(category_name="New Category")
        new_subcategory = ProductSubcategory.objects.create(
            category=new_category,
            subcategory_name="New Subcategory",
            subcategory_description="New Subcategory Description",
        )

        # Create a new product with the new subcategory that
        # will not be included in the search due to the filter
        Product.objects.create(
            product_name="Filtered Product",
            product_description="Filtered Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
            subcategory=new_subcategory,
        )

        data = {
            "search": "",
            "sort": "price-asc",
            "filters": json.dumps({"category": [product.subcategory.category.id]}),
        }
        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 200
        assert len(response.data["products"]) == 1
        assert response.data["products"][0]["product_name"] == product.product_name

    def test_valid_filter_non_list(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        data = {
            "search": "",
            "sort": "price-asc",
            "filters": json.dumps({"category": product.subcategory.category.id}),
        }
        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 200
        assert len(response.data["products"]) == 1
        assert response.data["products"][0]["product_name"] == product.product_name

    def test_valid_filter_no_product(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture

        new_category = ProductCategory.objects.create(category_name="New Category")

        data = {
            "search": "",
            "sort": "price-asc",
            "filters": json.dumps({"category": [new_category.id]}),
        }
        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 200
        assert len(response.data["products"]) == 0

    def test_valid_sort(self, customer_fixture, product_fixture):
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        new_product = Product.objects.create(
            product_name="Sorted Product",
            product_description="Sorted Product Description",
            properties={"color": "red", "size": "small"},
            prices={5: 10.0, 10: 5.0},
        )

        data = {"search": "", "sort": "name-asc", "filters": {}}

        response = customer_client.get(self.url, data, format="json")
        assert response.status_code == 200
        assert len(response.data["products"]) == 2
        assert response.data["products"][0]["product_name"] == new_product.product_name
        assert response.data["products"][1]["product_name"] == product.product_name
