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

    def test_for_different_ids(self, customer_fixture, seller_fixture):
        """Tests that ids are different for different users"""
        customer_user, _ = customer_fixture
        seller_user, _ = seller_fixture
        assert customer_user.id != seller_user.id

    def test_duplicate_id_is_regenerated(self, mocker):
        """Tests that a duplicate ID is regenerated"""
        user1 = CustomUser.objects.create(username="user1", email="user1@example.com")

        # Try creating a second user with the same ID
        user2 = CustomUser(username="user2", email="user2@example.com")
        user2.id = user1.id  # Force duplicate ID

        mocker.patch(
            "Accounts.models.generate_unique_id", return_value="NEW_UNIQUE_ID"
        )  # Mock unique ID generator

        user2.save()  # This should regenerate the ID

        assert user2.id == "NEW_UNIQUE_ID"  # ID should be different

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
        print(customer_user.__dict__)

        test_user = CustomUser(username="test_user", email=customer_user.email)
        with pytest.raises(IntegrityError) as error_message:
            test_user.save()

        assert str(error_message.value) == f"Email '{customer_user.email}' is already taken."

    def test_save_max_attempts_reached(self, mocker):
        """Tests that an IntegrityError is raised if max attempts are reached"""
        user_1 = CustomUser(username="user1", email="user1@example.com")
        user_1.id = "TEST_ID"
        user_1.save()

        user_2 = CustomUser(username="user2", email="user2@example.com")
        user_2.id = "TEST_ID"

        mocker.patch("Accounts.models.generate_unique_id", return_value="TEST_ID")

        with pytest.raises(IntegrityError) as error_message:
            user_2.save()

        assert str(error_message.value) == "Could not generate a unique id after 5 attempts"

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
