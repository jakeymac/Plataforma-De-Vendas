import pytest
from django.urls import reverse
from Accounts.views import is_admin

from Products.models import ProductCategory, ProductSubcategory, ProductTopSubcategory

@pytest.mark.django_db
class TestIsAdmin:
    """ Tests the is_admin function. """
    def test_is_admin(self, logged_in_admin):
        """ Tests if the is_admin function returns True for an admin user. """
        admin_user, _ = logged_in_admin
        assert is_admin(admin_user)

    def test_is_not_admin(self, logged_in_seller):
        """ Tests if the is_admin function returns False for a seller user. """
        seller_user, _ = logged_in_seller
        assert not is_admin(seller_user)

@pytest.mark.django_db
class TestAdminPortal:
    """Tests the admin_portal view."""

    def test_admin_portal_access_admin(self, logged_in_admin):
        """Ensure an admin user can access the admin portal."""
        admin_user, client = logged_in_admin
        # Create a category, subcategory, and top subcategory for setup to test that topsubcategories get queried.
        category = ProductCategory.objects.create(category_name="Test Category")
        subcategory = ProductSubcategory.objects.create(subcategory_name="Test Subcategory", category=category)
        ProductTopSubcategory.objects.create(order=1, subcategory=subcategory)

        response = client.get(reverse("admin_portal"))

        assert response.status_code == 200
        assert "categories_json" in response.context
        assert "subcategories_json" in response.context
        assert "products_json" in response.context
        assert "top_subcategory_1" in response.context
        assert "Accounts/admin_portal.html" in [t.name for t in response.templates]

    def test_admin_portal_access_denied_non_admin(self, logged_in_seller, logged_in_customer):
        """Ensure non-admin users cannot access the admin portal."""
        seller_user, seller_client = logged_in_seller
        customer_user, customer_client = logged_in_customer

        # Test seller access
        seller_response = seller_client.get(reverse("admin_portal"))
        assert seller_response.status_code == 302  # Redirected to login page
        assert "/login" in seller_response.url  # Ensures correct redirect

        # Test customer access
        customer_response = customer_client.get(reverse("admin_portal"))
        assert customer_response.status_code == 302  # Redirected to login
        assert "/login" in customer_response.url

    def test_admin_portal_access_denied_anonymous(self, anonymous_client):
        """Ensure unauthenticated users are redirected to login."""
        response = anonymous_client.get(reverse("admin_portal"))
        assert response.status_code == 302
        assert "/login" in response.url  # Ensures correct redirect

@pytest.mark.django_db
class TestLogoutView:
    """Tests the logout_view view."""

    def test_logout_view(self, logged_in_admin):
        """Ensure a logged in user can log out."""
        admin_user, client = logged_in_admin
        response = client.get(reverse("logout"))
        assert response.status_code == 302
        assert "/" in response.url


@pytest.mark.django_db
class TestLoginPage:
    """Tests the login_page view."""

    def test_login_page(self, client):
        """Ensure the login page is accessible."""
        response = client.get(reverse("login"))
        assert response.status_code == 200
        assert "Accounts/login.html" in [t.name for t in response.templates]

    def test_login_page_next_link(self, client):
        """Ensure the login page can accept a next link."""
        response = client.get(reverse("login") + "?next=/admin_portal")
        assert response.status_code == 200
        assert "Accounts/login.html" in [t.name for t in response.templates]
        assert "/admin_portal" in response.context["next_link"]

@pytest.mark.django_db
class TestRegisterAccountPage:
    """Tests the register_account_page view."""

    def test_register_account_page(self, client):
        """Ensure the register account page is accessible."""
        response = client.get(reverse("register_account"))
        assert response.status_code == 200
        assert "Accounts/register_account.html" in [t.name for t in response.templates]

@pytest.mark.django_db
class TestViewAccount:
    """Tests the view_account view."""

    def test_view_account_seller(self, logged_in_seller):
        """Ensure a logged in seller can view their account."""
        seller_user, client = logged_in_seller
        response = client.get(reverse("view_account"))
        assert response.status_code == 200
        assert "Accounts/view_seller_account.html" in [t.name for t in response.templates]

    def test_view_account_customer(self, logged_in_customer):
        """Ensure a logged in customer can view their account."""
        customer_user, client = logged_in_customer
        response = client.get(reverse("view_account"))
        assert response.status_code == 200
        assert "Accounts/view_customer_account.html" in [t.name for t in response.templates]

    def test_view_account_admin(self, logged_in_admin):
        """Ensure an admin user can view their account."""
        admin_user, client = logged_in_admin
        response = client.get(reverse("view_account"))
        assert response.status_code == 200
        assert "Accounts/view_admin_account.html" in [t.name for t in response.templates]

    def test_view_account_denied_anonymous(self, anonymous_client):
        """Ensure an unauthenticated user is redirected to login."""
        response = anonymous_client.get(reverse("view_account"))
        assert response.status_code == 302
        assert "/login" in response.url
