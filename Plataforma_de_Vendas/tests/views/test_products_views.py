import pytest
from core.helpers import convert_prices_dict
from django.urls import reverse
from Products.models import ProductImage
from Stores.models import Store


@pytest.mark.django_db
class TestAddProductView:
    """Tests the add_product_view view."""

    def test_add_product_view_seller(self, logged_in_seller):
        """Ensure a logged in seller can access the add product view."""
        seller_user, client = logged_in_seller
        response = client.get(reverse("add_new_product"))
        assert response.status_code == 200
        assert "products/add_new_product.html" in [t.name for t in response.templates]

    def test_add_product_view_admin(self, logged_in_admin):
        """Ensure a logged in admin can access the add product view."""
        admin_user, client = logged_in_admin
        response = client.get(reverse("add_new_product"))
        assert response.status_code == 200
        assert "products/add_new_product.html" in [t.name for t in response.templates]

    def test_add_product_view_customer(self, logged_in_customer):
        """Ensure a logged in customer cannot access the add product view."""
        customer_user, client = logged_in_customer
        response = client.get(reverse("add_new_product"))
        assert response.status_code == 403


@pytest.mark.django_db
class TestEditProductView:
    """Tests the edit_product_view view."""

    def test_edit_product_view_seller(self, logged_in_seller, product_fixture, store_fixture):
        """Ensure a logged in seller can access the edit product view."""
        seller_user, client = logged_in_seller
        store = store_fixture
        product, _ = product_fixture
        seller_user.store = store
        seller_user.save()
        response = client.get(reverse("edit_product", args=[product.id]))
        assert response.status_code == 200
        assert "products/edit_product.html" in [t.name for t in response.templates]

    def test_edit_product_view_admin(self, logged_in_admin, product_fixture):
        """Ensure a logged in admin can access the edit product view."""
        admin_user, client = logged_in_admin
        product, _ = product_fixture
        response = client.get(reverse("edit_product", args=[product.id]))
        assert response.status_code == 200
        assert "products/edit_product.html" in [t.name for t in response.templates]

    def test_edit_product_view_customer(self, logged_in_customer, product_fixture):
        """Ensure a logged in customer cannot access the edit product view."""
        customer_user, client = logged_in_customer
        product, _ = product_fixture
        response = client.get(reverse("edit_product", args=[product.id]))
        assert response.status_code == 403

    def test_edit_product_view_seller_not_own_product(
        self, logged_in_seller, product_fixture, store_fixture
    ):
        """Ensure a logged in seller cannot access the edit
        product view of a product not owned by them."""

        seller_user, client = logged_in_seller
        product, _ = product_fixture

        new_store = Store.objects.create(
            store_name="New Store",
            store_description="New Store Description",
        )

        seller_user.store = new_store
        seller_user.save()

        response = client.get(reverse("edit_product", args=[product.id]))
        assert response.status_code == 403

    def test_edit_product_view_nonexistent_product(self, logged_in_seller):
        """Ensure a logged in seller cannot access the edit
        product view of a nonexistent product."""
        seller_user, client = logged_in_seller
        response = client.get(reverse("edit_product", args=[9999]))
        assert response.status_code == 404


@pytest.mark.django_db
class TestViewProductView:
    """Tests the view_product_view view."""

    def test_view_product_view(self, logged_in_customer, product_fixture):
        """Ensure a logged in customer can access the view product view."""
        customer_user, client = logged_in_customer
        product, _ = product_fixture
        response = client.get(reverse("view_product", args=[product.id]))
        assert response.status_code == 200
        assert "products/view_product.html" in [t.name for t in response.templates]
        assert product.id == response.context["product"].id
        images = ProductImage.objects.filter(product=product).order_by("order")
        print(images)
        print(response.context["images"])
        assert list(images) == list(response.context["images"])
        assert product.prices == convert_prices_dict(response.context["prices"])

    def test_view_product_view_nonexistent_product(self, logged_in_customer):
        """Ensure a logged in customer cannot access the
        view product view of a nonexistent product."""
        customer_user, client = logged_in_customer
        response = client.get(reverse("view_product", args=[9999]))
        assert response.status_code == 404
