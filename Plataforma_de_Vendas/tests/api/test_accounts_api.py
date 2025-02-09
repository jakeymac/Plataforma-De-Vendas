import pytest
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db
class TestGetUsersEndpoint:
    """Tests the get_users_endpoint - api/accounts/ - all-users-endpoint"""

    url = reverse("all-users-endpoint")

    def test_admin_access(self, admin_fixture):
        """Admin should get a 200 OK response."""
        admin_user, admin_client = admin_fixture
        response = admin_client.get(self.url)
        assert response.status_code == 200

    def test_seller_access(self, seller_fixture):
        """Sellers should get a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        response = seller_client.get(self.url)
        assert response.status_code == 401

    def test_unauthenticated_access(self, anonymous_client):
        """Unauthenticated users should get a 403 Forbidden response."""
        response = anonymous_client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestGetUserEndpoint:
    """Tests the get_user_endpoint - api/accounts/<str:user_id>/ - user-by-id-endpoint"""

    def test_valid_admin_access(self, admin_fixture, random_user):
        """Admin should get a 200 OK response."""
        admin_user, admin_client = admin_fixture
        url = reverse("user-by-id-endpoint", kwargs={"user_id": random_user.id})
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_invalid_admin_access(self, admin_fixture):
        """Admin should get a 404 Not Found response."""
        admin_user, admin_client = admin_fixture
        url = reverse("user-by-id-endpoint", kwargs={"user_id": 999})
        response = admin_client.get(url)
        assert response.status_code == 404

    def test_invalid_seller_access(self, seller_fixture, random_user):
        """Sellers should get a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        url = reverse("user-by-id-endpoint", kwargs={"user_id": random_user.id})
        response = seller_client.get(url)
        assert response.status_code == 401

    def test_valid_seller_access(self, seller_fixture):
        """Sellers should get a 200 OK response."""
        seller_user, seller_client = seller_fixture
        url = reverse("user-by-id-endpoint", kwargs={"user_id": seller_user.id})
        response = seller_client.get(url)
        assert response.status_code == 200
        assert response.json()["username"] == seller_user.username

    def test_invalid_customer_access(self, customer_fixture, random_user):
        """Customers should get a 401 Unauthorized response."""
        customer_user, customer_client = customer_fixture
        url = reverse("user-by-id-endpoint", kwargs={"user_id": random_user.id})
        response = customer_client.get(url)
        assert response.status_code == 401

    def test_valid_customer_access(self, customer_fixture):
        """Customers should get a 200 OK response."""
        customer_user, customer_client = customer_fixture
        url = reverse("user-by-id-endpoint", kwargs={"user_id": customer_user.id})
        response = customer_client.get(url)
        assert response.status_code == 200
        assert response.json()["username"] == customer_user.username

    def test_unauthenticated_access(self, anonymous_client, random_user):
        """Unauthenticated users should get a 403 Forbidden response."""
        url = reverse("user-by-id-endpoint", kwargs={"user_id": random_user.id})
        response = anonymous_client.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestGetCustomersEndpoint:
    """Tests the get_customers_endpoint - api/accounts/customers/ - all-customers-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self, customer_group):
        self.customer_group = customer_group
        self.url = reverse("all-customers-endpoint")

    def test_admin_access(self, admin_fixture, customer_fixture):
        """Admin should get a 200 OK response."""
        admin_user, admin_client = admin_fixture
        customer_user, _ = customer_fixture
        response = admin_client.get(self.url)
        assert response.status_code == 200
        assert response.json()[0]["username"] == customer_user.username

    def test_seller_access(self, seller_fixture):
        """Sellers should get a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        response = seller_client.get(self.url)
        assert response.status_code == 401

    def test_unauthenticated_access(self, anonymous_client):
        """Unauthenticated users should get a 403 Forbidden response."""
        response = anonymous_client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestGetAdminsEndpoint:
    """Tests the get_admins_endpoint - api/accounts/admins/ - all-admins-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self, admin_group):
        self.admin_group = admin_group
        self.url = reverse("all-admins-endpoint")

    def test_admin_access(self, admin_fixture):
        """Admin should get a 200 OK response."""
        admin_user, admin_client = admin_fixture
        response = admin_client.get(self.url)
        assert response.status_code == 200
        assert response.json()[0]["username"] == admin_user.username

    def test_seller_access(self, seller_fixture):
        """Sellers should get a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        response = seller_client.get(self.url)
        assert response.status_code == 401

    def test_unauthenticated_access(self, anonymous_client):
        """Unauthenticated users should get a 403 Forbidden response."""
        response = anonymous_client.get(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestGetCurrentUserInfoEndpoint:
    """Tests the get_current_user_info_endpoint - api/accounts/current-user/ - current-user-endpoint"""

    url = reverse("current-user-endpoint")

    def test_valid_access(self, customer_fixture):
        """Authenticated users should get a 200 OK response."""
        customer_user, customer_client = customer_fixture
        response = customer_client.get(self.url)
        assert response.status_code == 200
        assert response.json()["username"] == customer_user.username

    def test_unauthenticated_access(self, anonymous_client):
        """Unauthenticated users should get a 403 Forbidden response."""
        response = anonymous_client.get(self.url)
        assert response.status_code == 403


class TestEditUserEndpoint:
    """Tests the edit_user_endpoint - api/accounts/edit_user/ - edit-user-endpoint"""

    def test_admin_access(self, admin_fixture, random_user):
        """Admin should get a 200 OK response."""
        admin_user, admin_client = admin_fixture
        url = reverse("edit-user-endpoint")
        data = {
            "id": random_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = admin_client.put(url, data, format="json")
        print(response.json())
        assert response.status_code == 200
        assert response.json()["user_info"]["username"] == data["username"]
        assert response.json()["user_info"]["first_name"] == data["first_name"]
        assert response.json()["user_info"]["last_name"] == data["last_name"]

    def test_valid_access(self, customer_fixture):
        """Authenticated users should get a 200 OK response."""
        customer_user, customer_client = customer_fixture
        url = reverse("edit-user-endpoint")
        data = {
            "id": customer_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = customer_client.put(url, data, format="json")
        print(response.json())
        assert response.status_code == 200
        assert response.json()["user_info"]["username"] == data["username"]
        assert response.json()["user_info"]["first_name"] == data["first_name"]
        assert response.json()["user_info"]["last_name"] == data["last_name"]

    def test_unauthenticated_access(self, anonymous_client, random_user):
        """Unauthenticated users should get a 403 Forbidden response."""
        url = reverse("edit-user-endpoint")
        data = {
            "id": random_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = anonymous_client.put(url, data, format="json")
        assert response.status_code == 403

    def test_invalid_access(self, seller_fixture, random_user):
        """Sellers should get a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        url = reverse("edit-user-endpoint")
        data = {
            "id": random_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = seller_client.put(url, data, format="json")
        assert response.status_code == 401

    def test_repeated_username(self, admin_fixture, random_user):
        """Should return a 400 Bad Request response."""
        admin_user, admin_client = admin_fixture
        url = reverse("edit-user-endpoint")
        data = {
            "id": random_user.id,
            "username": admin_user.username,
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = admin_client.put(url, data, format="json")
        assert response.status_code == 400
    
    def test_nonexisten_user_id(self, admin_fixture):
        """Should return a 404 Not Found response."""
        admin_user, admin_client = admin_fixture
        url = reverse("edit-user-endpoint")
        data = {
            "id": 999,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = admin_client.put(url, data, format="json")
        assert response.status_code == 404
