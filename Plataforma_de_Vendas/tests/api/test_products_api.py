import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from Products.models import (
    InitialProductImage,
    InitialProductState,
    Product,
    ProductImage,
    ProductSubcategory,
)


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
class TestSearchForProductEndpoint:
    """Test search_for_product_endpoint - api/products/search/store_id - search-product-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.no_store_view_name = "search-product-endpoint"
        self.store_view_name = "search-product-by-store-endpoint"

    ######################################
    # Tests searching without a store ID #
    ######################################

    def test_valid_search_no_store(self, customer_fixture, product_fixture):
        """Test that searching for a product by valid query returns correct results."""
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        # Perform the search query
        url = reverse(self.no_store_view_name) + "?q=test"
        response = customer_client.get(url)

        # Check if response contains product data
        assert response.status_code == 200
        assert len(response.data) > 0
        assert any(product["product_name"] == "Test Product Name" for product in response.data)

    def test_valid_search_no_results_no_store(self, customer_fixture, product_fixture):
        """Test that searching for a product by valid query returns no results."""
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture

        # Perform the search query
        url = reverse(self.no_store_view_name) + "?q=invalid"
        response = customer_client.get(url)

        # Check if response contains product data
        assert response.status_code == 200
        assert len(response.data) == 0

    ####################################
    # Tests searching with a store ID #
    ####################################

    def test_valid_search_with_store(self, store_fixture, customer_fixture, product_fixture):
        """Test that searching for a product by valid query returns correct results."""
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture
        store_id = store_fixture.id

        # Perform the search query
        url = reverse(self.store_view_name, kwargs={"store_id": store_id}) + "?q=test"
        response = customer_client.get(url)

        # Check if response contains product data
        assert response.status_code == 200
        assert len(response.data) > 0
        assert any(product["product_name"] == "Test Product Name" for product in response.data)

    def test_valid_search_no_results_with_store(
        self, store_fixture, customer_fixture, product_fixture
    ):
        """Test that searching for a product by valid query returns no results."""
        customer_user, customer_client = customer_fixture
        product, _ = product_fixture
        store_id = store_fixture.id

        # Perform the search query
        url = reverse(self.store_view_name, kwargs={"store_id": store_id}) + "?q=invalid"
        response = customer_client.get(url)

        # Check if response contains product data
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_valid_search_nonexistent_store(self, customer_fixture):
        """Test that searching for a product by valid query returns no results."""
        customer_user, customer_client = customer_fixture

        # Perform the search query
        url = reverse("search-product-by-store-endpoint", kwargs={"store_id": "0"}) + "?q=test"
        response = customer_client.get(url)

        # Check if response contains product data
        assert response.status_code == 404
        assert response.data["message"] == "Store not found with the id 0"


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
        assert not InitialProductImage.objects.filter(product=initial_product).exists()

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

    def test_first_iamge_added(self, admin_fixture):
        """Test adding a first image to a product to test the order attribute."""
        admin_user, admin_client = admin_fixture

        product = Product.objects.create(
            product_name="Test Product Name",
            product_description="Test Product Description",
            properties={"color": "red", "size": "small"},
            prices={"price": 10.0, "discount_price": 5.0},
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
