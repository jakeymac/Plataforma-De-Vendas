import pytest
from Accounts.models import CustomUser
from Accounts.serializers import is_phone_number_valid, is_country_code_valid, format_phone_number, CustomUserSerializer, ExistingUserSerializer
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory


@pytest.mark.django_db
class TestHelperFunctions:
    """ Test the helper functions for the CustomUser Serializers. """
    def test_invalid_brasil_phone_number_by_hyphens(self):
        """ Test that the function returns False for an invalid Brasil phone number by amount of hyphens. """
        phone_number = "1-23-45-67890"
        country_code = "55"

        assert not is_phone_number_valid(phone_number, country_code)

    def test_invalid_usa_phone_number_by_hyphens(self):
        """ Test that the function returns False for an invalid USA phone number by amount of hyphens. """
        phone_number = "123-456-7-8-90"
        country_code = "1"

        assert not is_phone_number_valid(phone_number, country_code)

    def test_invalid_brasil_number_by_amount(self):
        """ Test that the function returns False for an invalid Brasil phone number by amount of numbers. """
        phone_number = "123456789"
        country_code = "55"

        assert not is_phone_number_valid(phone_number, country_code)

    def test_invalid_usa_number_by_amount(self):
        """ Test that the function returns False for an invalid USA phone number by amount of numbers. """
        phone_number = "123456789"
        country_code = "1"

        assert not is_phone_number_valid(phone_number, country_code)

    def test_valid_brasil_phone_number(self):
        """ Test that the function returns True for a valid Brasil phone number. """
        phone_number = "12-3456-7890"
        country_code = "55"

        assert is_phone_number_valid(phone_number, country_code)

        phone_number = "1234567890"
        country_code = "55"
        assert is_phone_number_valid(phone_number, country_code)

    def test_valid_usa_phone_number(self):
        """ Test that the function returns True for a valid USA phone number. """
        phone_number = "123-456-7890"
        country_code = "1"

        assert is_phone_number_valid(phone_number, country_code)

        phone_number = "1234567890"
        country_code = "1"
        assert is_phone_number_valid(phone_number, country_code)

    def test_invalid_country_code(self):
        """ Test that the function returns False for an invalid country code. """
        country_code = "123"

        assert not is_country_code_valid(country_code)

    def test_valid_country_codes(self):
        """ Test that the function returns True for valid country codes. """
        country_code = "1"
        assert is_country_code_valid(country_code)

        country_code = "55"
        assert is_country_code_valid(country_code)

    def test_format_brasil_phone_number_10_digits(self):
        """ Test that the function formats a Brasil phone number with 10 digits. """
        phone_number = "1234567890"
        country_code = "55"

        assert format_phone_number(country_code, phone_number) == "(12) 3456-7890"

    def test_format_brasil_phone_number_11_digits(self):
        """ Test that the function formats a Brasil phone number with 11 digits. """
        phone_number = "12345678901"
        country_code = "55"

        assert format_phone_number(country_code, phone_number) == "(12) 34567-8901"

    def test_format_usa_phone_number(self):
        """ Test that the function formats a USA phone number. """
        phone_number = "1234567890"
        country_code = "1"

        assert format_phone_number(country_code, phone_number) == "(123) 456-7890"

@pytest.mark.django_db
class TestCustomUserValidate:
    """ Test the validate method of the CustomUserSerializer. """

    def test_no_request_context(self):
        """ Test that the method raises an error if there is no request context. """
        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "admin_user",
            "email": "admin_test@example.com",
            "password": "password123",
            "account_type": "admin",
        }

        serializer = CustomUserSerializer(data=data)

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
        
        assert "Request context is required for security purposes" in str(serializer.errors)
    
    def test_invalid_account_type(self):
        """ Test that the account type must be valid. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "admin_user",
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "invalid_account_type",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Invalid account type" in str(serializer.errors)

    def test_invalid_admin_creation(self):
        """ Test that only admins can create admin accounts. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "admin_user",
            "email": "admin_test@example.com",
            "password": "password123",
            "account_type": "admin",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
        
        assert "Only admins can create admin accounts" in str(serializer.errors)

    def test_username_already_exists(self, admin_fixture):
        """ Test that the username must be unique. """
        admin_user, _ = admin_fixture

        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": admin_user.username,
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "customer",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "A user with that username already exists." in str(serializer.errors)

    def test_email_already_exists(self, admin_fixture, customer_fixture):
        """ Test that the email must be unique. """
        admin_user, _ = admin_fixture

        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": admin_user.email,
            "password": "password123",
            "account_type": "customer",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "A user with that email already exists." in str(serializer.errors)

    def test_password_too_short(self):
        """ Test that the password must be at least 8 characters long. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": "test_email@example.com",
            "password": "short",
            "account_type": "customer",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Password must have at least 8 characters" in str(serializer.errors)
    
    def test_invalid_zip_code(self):
        """ Test that the zip code must be valid. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "customer",
            "zip_code": "123",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Invalid zip code" in str(serializer.errors)

    def test_invalid_country_code(self):
        """ Test that the country phone number code must be valid. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "customer",
            "phone_number": "123456789",
            "country_phone_number_code": "123",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Invalid country code" in str(serializer.errors)

    def test_invalid_phone_number(self):
        """ Test that the phone number must be valid. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "customer",
            "phone_number": "123",
            "country_phone_number_code": "1",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Invalid phone number" in str(serializer.errors)

    def test_seller_without_store(self):
        """ Test that a seller account must have a store. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "seller",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Seller account must have a store" in str(serializer.errors)

    def test_seller_with_nonexistent_store(self):
        """ Test that the store must exist. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "seller",
            "store": "1",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert not serializer.is_valid()
        assert "Store does not exist" in str(serializer.errors)
    
    def test_valid_account_creation(self, customer_group):
        """ Test that the serializer accepts valid data. """
        factory = APIRequestFactory()
        request = factory.post("")
        request.user = AnonymousUser()

        data = {
            "first_name": "Test_Name",
            "last_name": "Test_Last_Name",
            "username": "test_username",
            "email": "test_email@example.com",
            "password": "password123",
            "account_type": "customer",
            "phone_number": "1234567890",
            "country_phone_number_code": "1",
        }

        serializer = CustomUserSerializer(data=data, context={"request": request})
        assert serializer.is_valid()
        user = serializer.save()
        
        assert isinstance(user, CustomUser)
        assert user.username == data["username"]
        assert user.email == data["email"]
        assert user.first_name == data["first_name"]
        assert user.last_name == data["last_name"]
        assert user.check_password(data["password"])
        assert user.groups.filter(name="Customers").exists()

    
    @pytest.mark.django_db
    class TestExistingUserSerializer:
        """ Test the ExistingUserSerializer. """

        def test_no_request_context(self, customer_fixture):
            """ Test that the method raises an error if there is no request context. """
            customer_user, _ = customer_fixture

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": "customer_user",
                "password": "password123",
                "email": "test_email@example.com",
                "account_type": "customer",
            }

            serializer = ExistingUserSerializer(customer_user, data=data)

            with pytest.raises(ValidationError):
                serializer.is_valid(raise_exception=True)

            assert "Request context is required for security purposes" in str(serializer.errors)

        def test_customer_cannot_become_admin(self, customer_fixture, admin_group):
            """ Test that a customer cannot become an admin. """
            customer_user, _ = customer_fixture

            factory = APIRequestFactory()
            request = factory.post("")
            request.user = customer_user

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": "customer_user",
                "password": "password123",
                "email": "test_email@example.com",
                "account_type": "admin",
            }

            serializer = ExistingUserSerializer(customer_user, data=data, context={"request": request})
            assert not serializer.is_valid()
            assert "Only admins can create admin accounts" in str(serializer.errors)

        def test_username_already_exists(self, customer_fixture, admin_fixture):
            """ Test that the username must be unique. """
            customer_user, _ = customer_fixture
            admin_user, _ = admin_fixture

            factory = APIRequestFactory()
            request = factory.post("")
            request.user = customer_user

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": admin_user.username,
                "password": "password123",
                "email": "test_email@example.com",
                "account_type": "customer",
            }

            serializer = ExistingUserSerializer(customer_user, data=data, context={"request": request}) 
            assert not serializer.is_valid()
            assert "A user with that username already exists." in str(serializer.errors)

        def test_email_already_exists(self, customer_fixture, admin_fixture):
            """ Test that the email must be unique. """
            customer_user, _ = customer_fixture
            admin_user, _ = admin_fixture

            factory = APIRequestFactory()
            request = factory.post("")
            request.user = customer_user

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": "test_username",
                "password": "password123",
                "email": admin_user.email,
                "account_type": "customer",
            }

            serializer = ExistingUserSerializer(customer_user, data=data, context={"request": request})
            assert not serializer.is_valid()
            assert "A user with that email already exists." in str(serializer.errors)

        def test_password_too_short(self, customer_fixture):
            """ Test that the password must be at least 8 characters long. """
            customer_user, _ = customer_fixture

            factory = APIRequestFactory()
            request = factory.post("")
            request.user = customer_user

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": "test_username",
                "password": "short",
                "email": "test_email@example.com",
                "account_type": "customer",
            }

            serializer = ExistingUserSerializer(customer_user, data=data, context={"request": request})
            assert not serializer.is_valid()
            assert "Password must have at least 8 characters" in str(serializer.errors)
            
        def test_invalid_zip_code(self, customer_fixture):
            """ Test that the zip code must be valid. """
            customer_user, _ = customer_fixture

            factory = APIRequestFactory()
            request = factory.post("")
            request.user = customer_user

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": "test_username",
                "password": "password123",
                "email": "test_email@example.com",
                "account_type": "customer",
                "zip_code": "123",
            }

            serializer = ExistingUserSerializer(customer_user, data=data, context={"request": request})
            assert not serializer.is_valid()
            assert "Invalid zip code" in str(serializer.errors)

        def test_invalid_phone_number(self, customer_fixture):
            """ Test that the phone number must be valid. """
            customer_user, _ = customer_fixture

            factory = APIRequestFactory()
            request = factory.post("")
            request.user = customer_user

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": "test_username",
                "password": "password123",
                "email": "test_email@example.com",
                "account_type": "customer",
                "phone_number": "123",
                "country_phone_number_code": "1",
            }

            serializer = ExistingUserSerializer(customer_user, data=data, context={"request": request})
            assert not serializer.is_valid()
            assert "Invalid phone number" in str(serializer.errors)

        def test_new_account(self):
            """ Test that the serializer creates a new account. """
            factory = APIRequestFactory()
            request = factory.post("")
            request.user = AnonymousUser()

            data = {
                "first_name": "Test_Name",
                "last_name": "Test_Last_Name",
                "username": "test_username",
                "password": "password123",
                "email": "test_email@example.com",
                "account_type": "customer",
                "phone_number": "1234567890",
                "country_phone_number_code": "1",
            }

            serializer = ExistingUserSerializer(data=data, context={"request": request})
            assert not serializer.is_valid()
            assert "Serializer only to be used for existing users" in str(serializer.errors)

        def test_valid_account_update(self, customer_fixture):
            """ Test that the serializer accepts valid data. """
            customer_user, _ = customer_fixture

            factory = APIRequestFactory()
            request = factory.post("")
            request.user = customer_user

            data = {
                "first_name": "New_First_Name",
                "last_name": "New_Last_Name",
                "username": "new_username",
                "password": "new_password123",
                "email": "new_email@example.com",
                "account_type": "customer",
                "phone_number": "1234567890",
                "country_phone_number_code": "1",
                "zip_code": "12345",
            }

            serializer = ExistingUserSerializer(customer_user, data=data, context={"request": request})
            assert serializer.is_valid()
            user = serializer.save()
            
            assert isinstance(user, CustomUser)
            assert user.username == data["username"]
            assert user.email == data["email"]
            assert user.first_name == data["first_name"]
            assert user.last_name == data["last_name"]
            assert user.check_password(data["password"])
            assert user.groups.filter(name="Customers").exists()
            assert user.zip_code == data["zip_code"]
            assert user.phone_number == format_phone_number(data["country_phone_number_code"], data["phone_number"])

