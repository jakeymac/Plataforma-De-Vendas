from unittest import mock

import pytest
from Accounts.models import CustomUser
from django.db.utils import IntegrityError


@pytest.mark.django_db
class TestCustomUserSave:
    """Tests the CustomUser.save method"""

    def test_normal_save(self, customer_fixture):
        """Tests a normal save"""
        customer_user, _ = customer_fixture
        customer_user.save()
        assert customer_user.id is not None

    def test_duplicate_username(self, customer_fixture):
        """Tests that a duplicate username raises an IntegrityError"""
        customer_user, _ = customer_fixture

        test_user = CustomUser(username=customer_user.username, email="test_user@example.com")
        with pytest.raises(IntegrityError) as error_message:
            test_user.save()

        assert str(error_message.value) == f"Username '{customer_user.username}' is already taken."

    def test_duplicate_email(self, customer_fixture):
        """Tests that a duplicate email raises an IntegrityError"""
        customer_user, _ = customer_fixture

        test_user = CustomUser(username="test_user", email=customer_user.email)
        with pytest.raises(IntegrityError) as error_message:
            test_user.save()

        assert str(error_message.value) == f"Email '{customer_user.email}' is already taken."

    def test_custom_user_generic_integrity_error(self, customer_fixture):
        customer_user, _ = customer_fixture
        with mock.patch(
            "core.models.UniqueIDModel.save", side_effect=IntegrityError("Generic error")
        ):
            with pytest.raises(IntegrityError) as e:
                customer_user.save()

            assert str(e.value) == "Generic error"

    def test_str(self, customer_fixture):
        """Tests the __str__ method"""
        customer_user, _ = customer_fixture
        assert str(customer_user) == customer_user.username

    def test_is_customer(self, customer_fixture):
        """Tests the is_customer method"""
        customer_user, _ = customer_fixture
        assert customer_user.is_customer()

    def test_is_seller(self, seller_fixture):
        """Tests the is_seller method"""
        seller_user, _ = seller_fixture
        assert seller_user.is_seller()

    def test_is_admin(self, admin_fixture):
        """Tests the is_admin method"""
        admin_user, _ = admin_fixture
        assert admin_user.is_admin()

    def test_is_not_customer(self, seller_fixture):
        """Tests the is_customer method"""
        seller_user, _ = seller_fixture
        assert not seller_user.is_customer()

    def test_is_not_seller(self, customer_fixture):
        """Tests the is_seller method"""
        customer_user, _ = customer_fixture
        assert not customer_user.is_seller()

    def test_is_not_admin(self, customer_fixture):
        """Tests the is_admin method"""
        customer_user, _ = customer_fixture
        assert not customer_user.is_admin()
