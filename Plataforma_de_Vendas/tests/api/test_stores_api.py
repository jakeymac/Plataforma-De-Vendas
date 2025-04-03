import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime
from io import BytesIO
from PIL import Image

from Accounts.models import CustomUser
from Stores.models import Store
from Stores.endpoints import parse_store_registration_data

# Helper function for generating test image files
def generate_test_image_file(name="test.jpg"):
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/jpeg")


class TestParseStoreRegistrationData:
    def test_parse_store_registration_data_full_valid(self):
        dob = "1990-01-01"
        profile_pic = SimpleUploadedFile("profile.jpg", b"file_content")
        store_logo = SimpleUploadedFile("logo.jpg", b"logo_content")

        request_data = {
            "username": "testuser",
            "password": "securepass123",
            "email": "test@example.com",
            "first_name": "Testy",
            "last_name": "McTestface",
            "date_of_birth": dob,
            "phone_number": "1234567890",
            "country_phone_number_code": "+1",
            "address": "123 Main St",
            "address_line_two": "Apt 4",
            "city": "Metropolis",
            "state": "Testonia",
            "country": "Testland",
            "zip_code": "00001",
            "store_name": "Test Store",
            "store_description": "A store for testing",
            "store_url": "teststore",
        }

        request_files = {
            "profile_picture": profile_pic,
            "store_logo": store_logo,
        }

        account_data, store_data = parse_store_registration_data(request_data, request_files)

        assert account_data["username"] == "testuser"
        assert account_data["date_of_birth"] == "1990-01-01"
        assert account_data["profile_picture"] == profile_pic
        assert store_data["store_logo"] == store_logo
        assert store_data["store_name"] == "Test Store"

    def test_parse_store_registration_data_no_dob(self):
        profile_pic = SimpleUploadedFile("profile.jpg", b"file_content")
        store_logo = SimpleUploadedFile("logo.jpg", b"logo_content")

        request_data = {
            "username": "testuser",
            "password": "securepass123",
            "email": "test@example.com",
            "first_name": "Testy",
            "last_name": "McTestface",
            "date_of_birth": None,
            "phone_number": "1234567890",
            "country_phone_number_code": "+1",
            "address": "123 Main St",
            "address_line_two": "Apt 4",
            "city": "Metropolis",
            "state": "Testonia",
            "country": "Testland",
            "zip_code": "00001",
            "store_name": "Test Store",
            "store_description": "A store for testing",
            "store_url": "teststore",
        }
        request_files = {
            "profile_picture": profile_pic,
            "store_logo": store_logo,
        }

        account_data, store_data = parse_store_registration_data(request_data, request_files)
        
        assert account_data["date_of_birth"] is None
        assert account_data["username"] == "testuser"
        assert account_data["profile_picture"] == profile_pic
        assert store_data["store_logo"] == store_logo
        assert store_data["store_name"] == "Test Store"

    def test_parse_store_registration_data_dob_as_date_object(self):
        profile_pic = SimpleUploadedFile("profile.jpg", b"file_content")
        store_logo = SimpleUploadedFile("logo.jpg", b"logo_content")

        request_data = {
            "username": "testuser",
            "password": "securepass123",
            "email": "test@example.com",
            "first_name": "Testy",
            "last_name": "McTestface",
            "date_of_birth": datetime(1985, 5, 12),
            "phone_number": "1234567890",
            "country_phone_number_code": "+1",
            "address": "123 Main St",
            "address_line_two": "Apt 4",
            "city": "Metropolis",
            "state": "Testonia",
            "country": "Testland",
            "zip_code": "00001",
            "store_name": "Test Store",
            "store_description": "A store for testing",
            "store_url": "teststore",
        }
        request_files = {
            "profile_picture": profile_pic,
            "store_logo": store_logo,
        }

        account_data, store_data = parse_store_registration_data(request_data, request_files)
        
        assert account_data["date_of_birth"] == "1985-05-12"
        assert account_data["username"] == "testuser"
        assert account_data["profile_picture"] == profile_pic
        assert store_data["store_logo"] == store_logo
        assert store_data["store_name"] == "Test Store"

class TestGetStoreEndpoint:
    """ Test class for the get_store_endpoint - api/stores/store_id - store-by-id-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "store-by-id-endpoint"

    def test_valid_access(self, customer_fixture, store_fixture):
        """ Test valid access to the endpoint """
        customer_user, customer_client = customer_fixture
        store = store_fixture

        url = reverse(self.view_name, kwargs={"store_id": store.id})

        response = customer_client.get(url)
        
        assert response.status_code == 200
        assert response.data["id"] == store.id
        assert response.data["store_name"] == store.store_name
        assert response.data["store_description"] == store.store_description
        assert response.data["store_url"] == store.store_url

    def test_non_existent_store(self, customer_fixture):
        """ Test invalid access to the endpoint """
        customer_user, customer_client = customer_fixture

        url = reverse(self.view_name, kwargs={"store_id": "0"})

        response = customer_client.get(url)
        assert response.status_code == 404
        assert response.data["message"] == "Store not found with the id 0"

class TestGetStoresEndpoint:
    """ Test class for the get_stores_endpoint - api/stores/add - add-store-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.view_name = "all-stores-endpoint"

    def test_valid_access(self, customer_fixture, store_fixture):
        """ Test valid access to the endpoint """
        customer_user, customer_client = customer_fixture
        store = store_fixture

        url = reverse(self.view_name)

        response = customer_client.get(url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == store.id
        assert response.data[0]["store_name"] == store.store_name
        assert response.data[0]["store_description"] == store.store_description
        assert response.data[0]["store_url"] == store.store_url

@pytest.mark.django_db
class TestUpdateStoreEndpoint:
    """ Test class for the update_store_endpoint - api/stores/update - update-store-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("update-store-endpoint")

    def test_valid_admin_access(self, admin_fixture, store_fixture):
        admin_user, admin_client = admin_fixture
        store = store_fixture

        data = {
            "id": store.id,
            "store_name": "Updated Store Name",
            "store_description": "Updated Store Description",
            "store_url": "updated_url",
        }

        response = admin_client.put(self.url, data=data, format="json")

        assert response.status_code == 200
        assert response.data["message"] == "Store updated successfully"
        assert response.data["store_name"] == data["store_name"]
        assert response.data["store_description"] == data["store_description"]
        assert response.data["store_url"] == data["store_url"]

    def test_valid_seller_access(self, seller_fixture, store_fixture):
        seller_user, seller_client = seller_fixture
        store = store_fixture

        data = {
            "id": store.id,
            "store_name": "Updated Store Name",
            "store_description": "Updated Store Description",
            "store_url": "updated_url",
        }

        response = seller_client.put(self.url, data=data, format="json")

        assert response.status_code == 200
        assert response.data["message"] == "Store updated successfully"
        assert response.data["store_name"] == data["store_name"]
        assert response.data["store_description"] == data["store_description"]
        assert response.data["store_url"] == data["store_url"]

    def test_invalid_access(self, customer_fixture, store_fixture):
        customer_user, customer_client = customer_fixture
        store = store_fixture

        data = {
            "id": store.id,
            "store_name": "Updated Store Name",
            "store_description": "Updated Store Description",
            "store_url": "updated_url",
        }

        response = customer_client.put(self.url, data=data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You are not authorized to update stores"
        
    def test_unauthorized_seller_account(self, seller_fixture):
        """ Test for sellers that aren't part of the targeted store """
        seller_user, seller_client = seller_fixture
        
        new_store = Store.objects.create(
            store_name="New Store",
            store_description="New Store Description",
            store_url="new_store_url",
        )

        data = {
            "id": new_store.id,
            "store_name": "Updated Store Name",
            "store_description": "Updated Store Description",
            "store_url": "updated_url",
        }

        response = seller_client.put(self.url, data=data, format="json")

        assert response.status_code == 403
        assert response.data["message"] == "You are not authorized to update this store"
    
    def test_already_existing_store_name(self, admin_fixture, store_fixture):
        admin_user, admin_client = admin_fixture
        store = store_fixture

        new_store = Store.objects.create(
            store_name="New Store",
            store_description="New Store Description",
            store_url="new_store_url",
        )
        data = {
            "id": new_store.id,
            "store_name": store.store_name,
            "store_description": "Updated Store Description",
            "store_url": "updated_url",
        }

        response = admin_client.put(self.url, data=data, format="json")

        assert response.status_code == 400
        assert "A store with this name already exists." in response.data["store_name"][0]

    def test_invalid_store_id(self, admin_fixture):
        admin_user, admin_client = admin_fixture

        data = {
            "id": "0",
            "store_name": "Updated Store Name",
            "store_description": "Updated Store Description",
            "store_url": "updated_url",
        }

        response = admin_client.put(self.url, data=data, format="json")

        assert response.status_code == 404
        assert response.data["message"] == "Store not found with the id 0"

@pytest.mark.django_db
class TestRegisterStoreEndpoint:
    """ Test class for the register_store_endpoint - api/stores/register - register-store-endpoint """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse("register-store-endpoint")

    def get_valid_data(self):
        return {
            "username": "testuser",
            "password": "securepass123",
            "email": "test@example.com",
            "first_name": "Testy",
            "last_name": "McTestface",
            "date_of_birth": "1990-01-01",
            "phone_number": "1234567890",
            "country_phone_number_code": "1",
            "address": "123 Main St",
            "address_line_two": "Apt 4",
            "city": "Metropolis",
            "state": "Testonia",
            "country": "Testland",
            "zip_code": "00001",
            "store_name": "Test Store",
            "store_description": "A test store description",
            "store_url": "teststore",
        }

    def get_valid_files(self):
        return {
            "profile_picture": generate_test_image_file("profile.jpg"),
            "store_logo": generate_test_image_file("logo.jpg"),
        }

    def test_valid_access(self, anonymous_client):
        data = self.get_valid_data()
        files = self.get_valid_files()

        response = anonymous_client.post(self.url, data={**data, **files})

        assert response.status_code == 201
        assert response.data["message"] == "Store created successfully"
        assert CustomUser.objects.filter(username=data["username"]).exists()
        assert Store.objects.filter(store_name=data["store_name"]).exists()

    def test_missing_account_field(self, anonymous_client):
        data = self.get_valid_data()
        files = self.get_valid_files()

        # Remove the 'username' field
        del data["username"]

        response = anonymous_client.post(self.url, data={**data, **files})

        assert response.status_code == 400
        assert response.data["message"] == "Store not created"
        assert "This field may not be null." in response.data["errors"]["account_errors"]["username"][0]

    def test_missing_store_field(self, anonymous_client):
        data = self.get_valid_data()
        files = self.get_valid_files()

        # Remove the 'store_name' field
        del data["store_name"]

        response = anonymous_client.post(self.url, data={**data, **files})

        assert response.status_code == 400
        assert response.data["message"] == "Store not created"
        assert "This field may not be null." in response.data["errors"]["store_errors"]["store_name"][0]