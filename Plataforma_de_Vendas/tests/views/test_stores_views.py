import pytest
from django.urls import reverse
from Products.models import ProductTopSubcategory


@pytest.mark.django_db
class TestHomeView:
    """Test the home view"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("index")

    def test_home_view(self, client, category_fixture, subcategory_fixture):
        """Test the home view"""
        response = client.get(self.url)

        assert response.status_code == 200

        assert "Stores/home.html" in [t.name for t in response.templates]
        assert category_fixture.category_name in response.context["categories"]

        top_subcategory = ProductTopSubcategory.objects.get(subcategory=subcategory_fixture)
        assert top_subcategory in response.context["top_subcategories"]


@pytest.mark.django_db
class TestViewMyStoreView:
    """Test the view my store view"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("view_my_store")

    def test_valid_access(self, logged_in_seller, store_fixture):
        """Test the valid access to the view my store view"""
        seller_user, seller_client = logged_in_seller
        store = store_fixture
        seller_user.store = store
        seller_user.save()

        response = seller_client.get(self.url)

        assert response.status_code == 302
        assert response.url == f"/view_store/{store.store_url}/"

    def test_seller_with_no_store(self, logged_in_seller):
        """Test the access to the view my store view when the seller has no store"""
        _, seller_client = logged_in_seller
        response = seller_client.get(self.url)
        assert response.status_code == 404
        print(response.templates)
        assert b"There was an error finding your store." in response.content

    def test_non_seller_access(self, logged_in_customer):
        """Test the access to the view my store view when the user is not a seller"""
        _, customer_client = logged_in_customer
        response = customer_client.get(self.url, follow=True)  # follow to get to template
        assert response.status_code == 403
        assert "need to register as a seller first.".encode("utf-8") in response.content


class TestViewStoreView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "view_store"

    def test_valid_access(self, anonymous_client, store_fixture):
        """Test the view store view"""
        url = reverse(self.view_name, args=[store_fixture.store_url])
        response = anonymous_client.get(url)

        assert response.status_code == 200
        assert "Stores/view_store.html" in [t.name for t in response.templates]

    def test_invalid_store_url(self, anonymous_client):
        url = reverse(self.view_name, args=["invalid_store_url"])
        response = anonymous_client.get(url)
        assert response.status_code == 404
        assert b"The store you are looking for does not exist." in response.content

class TestRegisterStorePageView:
    """Test the register store page view"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("register_store")

    def test_register_store_page_view(self, anonymous_client):
        """Test the register store page view"""
        response = anonymous_client.get(self.url)

        assert response.status_code == 200
        assert "Stores/register_store.html" in [t.name for t in response.templates]
