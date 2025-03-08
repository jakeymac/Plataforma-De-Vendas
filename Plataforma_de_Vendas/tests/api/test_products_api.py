import pytest
from unittest.mock import patch
from django.urls import reverse
from Products.models import (
    InitialProductImage,
    InitialProductState,
    Product,
    ProductImage,
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

    def test_valid_search_no_results_with_store(self, store_fixture, customer_fixture, product_fixture):
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
