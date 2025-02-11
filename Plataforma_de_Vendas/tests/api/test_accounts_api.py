from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestGetUsersEndpoint:
    """Tests the get_users_endpoint - api/accounts/ - all-users-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("all-users-endpoint")

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

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "user-by-id-endpoint"

    def test_valid_admin_access(self, admin_fixture, random_user):
        """Admin should get a 200 OK response."""
        admin_user, admin_client = admin_fixture
        url = reverse(self.view_name, kwargs={"user_id": random_user.id})
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_invalid_admin_access(self, admin_fixture):
        """Admin should get a 404 Not Found response."""
        admin_user, admin_client = admin_fixture
        url = reverse(self.view_name, kwargs={"user_id": 999})
        response = admin_client.get(url)
        assert response.status_code == 404

    def test_invalid_seller_access(self, seller_fixture, random_user):
        """Sellers should get a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        url = reverse(self.view_name, kwargs={"user_id": random_user.id})
        response = seller_client.get(url)
        assert response.status_code == 401

    def test_valid_seller_access(self, seller_fixture):
        """Sellers should get a 200 OK response."""
        seller_user, seller_client = seller_fixture
        url = reverse(self.view_name, kwargs={"user_id": seller_user.id})
        response = seller_client.get(url)
        assert response.status_code == 200
        assert response.json()["username"] == seller_user.username

    def test_invalid_customer_access(self, customer_fixture, random_user):
        """Customers should get a 401 Unauthorized response."""
        customer_user, customer_client = customer_fixture
        url = reverse(self.view_name, kwargs={"user_id": random_user.id})
        response = customer_client.get(url)
        assert response.status_code == 401

    def test_valid_customer_access(self, customer_fixture):
        """Customers should get a 200 OK response."""
        customer_user, customer_client = customer_fixture
        url = reverse(self.view_name, kwargs={"user_id": customer_user.id})
        response = customer_client.get(url)
        assert response.status_code == 200
        assert response.json()["username"] == customer_user.username

    def test_unauthenticated_access(self, anonymous_client, random_user):
        """Unauthenticated users should get a 403 Forbidden response."""
        url = reverse(self.view_name, kwargs={"user_id": random_user.id})
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
    """Tests the get_current_user_info_endpoint - api/accounts/current-user/ -
    current-user-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("current-user-endpoint")

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

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("edit-user-endpoint")

    def test_admin_access(self, admin_fixture, random_user):
        """Admin should get a 200 OK response."""
        admin_user, admin_client = admin_fixture
        data = {
            "id": random_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = admin_client.put(self.url, data, format="json")
        assert response.status_code == 200
        assert response.json()["user_info"]["username"] == data["username"]
        assert response.json()["user_info"]["first_name"] == data["first_name"]
        assert response.json()["user_info"]["last_name"] == data["last_name"]

    def test_valid_access(self, customer_fixture):
        """Authenticated users should get a 200 OK response."""
        customer_user, customer_client = customer_fixture
        data = {
            "id": customer_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = customer_client.put(self.url, data, format="json")
        assert response.status_code == 200
        assert response.json()["user_info"]["username"] == data["username"]
        assert response.json()["user_info"]["first_name"] == data["first_name"]
        assert response.json()["user_info"]["last_name"] == data["last_name"]

    def test_unauthenticated_access(self, anonymous_client, random_user):
        """Unauthenticated users should get a 403 Forbidden response."""
        data = {
            "id": random_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = anonymous_client.put(self.url, data, format="json")
        assert response.status_code == 403

    def test_invalid_access(self, seller_fixture, random_user):
        """Sellers should get a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        data = {
            "id": random_user.id,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = seller_client.put(self.url, data, format="json")
        assert response.status_code == 401

    def test_repeated_username(self, admin_fixture, random_user):
        """Should return a 400 Bad Request response."""
        admin_user, admin_client = admin_fixture
        data = {
            "id": random_user.id,
            "username": admin_user.username,
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = admin_client.put(self.url, data, format="json")
        assert response.status_code == 400

    def test_nonexistent_user_id(self, admin_fixture):
        """Should return a 404 Not Found response."""
        admin_user, admin_client = admin_fixture
        data = {
            "id": 999,
            "username": "new_username",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
        }
        response = admin_client.put(self.url, data, format="json")
        assert response.status_code == 404


class TestLoginEndpoint:
    """Tests the login_endpoint - api/accounts/login/ - login-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("login-endpoint")

    def test_valid_login(self, customer_fixture):
        """Should return a 200 OK response."""
        customer_user, customer_client = customer_fixture
        url = reverse("login-endpoint")
        data = {
            "username": customer_user.username,
            "password": "password123",
        }
        response = customer_client.post(url, data, format="json")
        assert response.status_code == 200

    def test_invalid_login(self, customer_fixture):
        """Should return a 400 Bad Request response."""
        customer_user, customer_client = customer_fixture
        url = reverse("login-endpoint")
        data = {
            "username": customer_user.username,
            "password": "wrong_password",
        }
        response = customer_client.post(url, data, format="json")
        assert response.status_code == 401

    def test_missing_credentials(self, customer_fixture):
        """Should return a 400 Bad Request response."""
        customer_user, customer_client = customer_fixture
        url = reverse("login-endpoint")
        data = {}
        response = customer_client.post(url, data, format="json")
        assert response.status_code == 400

    def test_missing_username(self, customer_fixture):
        """Should return a 400 Bad Request response."""
        customer_user, customer_client = customer_fixture
        url = reverse("login-endpoint")
        data = {
            "password": "password123",
        }
        response = customer_client.post(url, data, format="json")
        assert response.status_code == 400

    def test_missing_password(self, customer_fixture):
        """Should return a 400 Bad Request response."""
        customer_user, customer_client = customer_fixture
        url = reverse("login-endpoint")
        data = {
            "username": customer_user.username,
        }
        response = customer_client.post(url, data, format="json")
        assert response.status_code == 400


class TestLogoutEndpoint:
    """Tests the logout_endpoint - api/accounts/logout/ - logout-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("logout-endpoint")

    def test_valid_logout(self, customer_fixture):
        """Should return a 200 OK response."""
        customer_user, customer_client = customer_fixture
        url = reverse("logout-endpoint")
        response = customer_client.get(url)
        assert response.status_code == 200


class TestRegisterCustomerEndpoint:
    """Tests the register_customer_account_endpoint - api/accounts/register/ -
    register-customer-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self, customer_group, seller_group):
        self.customer_group = customer_group
        self.seller_group = seller_group
        self.url = reverse("register-customer-endpoint")

    def test_valid_registration(self, anonymous_client):
        """Should return a 201 Created response."""
        url = reverse("register-customer-endpoint")
        data = {
            "username": "new_customer",
            "password": "password123",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
            "account_type": "customer",
        }
        response = anonymous_client.post(url, data, format="json")
        assert response.status_code == 201

    def test_missing_credentials(self, anonymous_client):
        """Should return a 400 Bad Request response."""
        url = reverse("register-customer-endpoint")
        data = {
            "username": "new_customer",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
            "account_type": "customer",
        }
        response = anonymous_client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json()["password"][0] == "This field is required."

    def test_already_existing_username(self, anonymous_client, customer_fixture):
        """Should return a 400 Bad Request response."""
        customer_user, _ = customer_fixture
        url = reverse("register-customer-endpoint")
        data = {
            "username": customer_user.username,
            "password": "password123",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
            "account_type": "customer",
        }
        response = anonymous_client.post(url, data, format="json")
        assert response.status_code == 400
        assert response.json()["username"][0] == "A user with that username already exists."

    def test_seller_account_creation(self, anonymous_client):
        """Should return a 400 Bad Request response."""
        url = reverse("register-customer-endpoint")
        data = {
            "username": "new_customer",
            "password": "password123",
            "first_name": "new_first_name",
            "last_name": "new_last_name",
            "account_type": "seller",
        }
        response = anonymous_client.post(url, data, format="json")
        assert response.status_code == 400


class TestCheckUsernameAvailabilityEndpoint:
    """Tests the check_username_availability_endpoint - api/accounts/username_available/ -
    username-availability-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("username-availability-endpoint")

    def test_valid_username(self, anonymous_client, customer_fixture):
        """Should return a 200 OK response."""
        customer_user, _ = customer_fixture  # Ensure we have a user in the database
        data = {"username": "new_username"}
        response = anonymous_client.post(self.url, data, format="json")
        assert response.status_code == 200
        assert response.json()["is_available"]

    def test_invalid_username(self, anonymous_client, seller_fixture):
        """Should return a 200 OK response."""
        seller_user, _ = seller_fixture
        data = {"username": seller_user.username}
        response = anonymous_client.post(self.url, data, format="json")
        assert response.status_code == 200
        assert not response.json()["is_available"]


class TestCheckEmailAvailabilityEndpoint:
    """Tests the check_email_availability_endpoint - api/accounts/email_available/ -
    email-availability-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("email-availability-endpoint")

    def test_valid_email(self, anonymous_client, seller_fixture):
        """Should return a 200 OK response."""
        seller_user, _ = seller_fixture  # Ensure we have a user in the database
        data = {"email": "new_email@gmail.com"}
        response = anonymous_client.post(self.url, data, format="json")
        assert response.status_code == 200
        assert response.json()["is_available"]

    def test_invalid_email(self, anonymous_client, customer_fixture):
        """Should return a 200 OK response."""
        customer_user, _ = customer_fixture
        data = {"email": customer_user.email}
        response = anonymous_client.post(self.url, data, format="json")
        assert response.status_code == 200
        assert not response.json()["is_available"]


class TestUpdateProfilePictureEndpoint:
    """Tests the update_profile_picture_endpoint - api/accounts/update_profile_picture/ -
    update-profile-picture-endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("update-profile-picture-endpoint")

    def test_valid_profile_picture(self, customer_fixture):
        """Should return a 200 OK response."""
        customer_user, customer_client = customer_fixture
        image = SimpleUploadedFile("image.jpg", b"file_content", content_type="image/jpeg")
        data = {"id": customer_user.id, "profile_picture": image}
        response = customer_client.put(self.url, data, format="multipart")
        assert response.status_code == 200

    @patch("django.db.models.fields.files.FieldFile.delete")  # Mock profile picture deletion
    def test_existing_picture_is_deleted(self, mock_delete, customer_fixture):
        """Test that an existing profile picture is deleted before a new one is uploaded."""
        customer_user, customer_client = customer_fixture
        customer_user.profile_picture = SimpleUploadedFile(
            "old.jpg", b"old_content", content_type="image/jpeg"
        )
        customer_user.save()

        image = SimpleUploadedFile("new.jpg", b"new_content", content_type="image/jpeg")
        data = {"id": str(customer_user.id), "profile_picture": image}
        response = customer_client.put(self.url, data, format="multipart")
        assert response.status_code == status.HTTP_200_OK
        # Ensure delete() was called to delete the old profile picture
        mock_delete.assert_called_once()

    def test_valid_admin_profile_picture(self, admin_fixture, customer_fixture):
        """Should return a 200 OK response."""
        admin_user, admin_client = admin_fixture
        customer_user, _ = customer_fixture
        image = SimpleUploadedFile("image.jpg", b"file_content", content_type="image/jpeg")
        data = {"id": customer_user.id, "profile_picture": image}
        response = admin_client.put(self.url, data, format="multipart")
        assert response.status_code == 200

    def test_invalid_customer_profile_picture(self, seller_fixture, customer_fixture):
        """Should return a 401 Unauthorized response."""
        seller_user, seller_client = seller_fixture
        customer_user, _ = customer_fixture
        image = SimpleUploadedFile("image.jpg", b"file_content", content_type="image/jpeg")
        data = {"id": customer_user.id, "profile_picture": image}
        response = seller_client.put(self.url, data, format="multipart")
        assert response.status_code == 401
        assert (
            response.json()["message"]
            == "You are not authorized to update this account's profile picture."
        )

    def test_unauthenticated_profile_picture(self, anonymous_client, customer_fixture):
        """Should return a 403 Forbidden response."""
        customer_user, _ = customer_fixture
        image = SimpleUploadedFile("image.jpg", b"file_content", content_type="image/jpeg")
        data = {"id": customer_user.id, "profile_picture": image}
        response = anonymous_client.put(self.url, data, format="multipart")
        assert response.status_code == 403
