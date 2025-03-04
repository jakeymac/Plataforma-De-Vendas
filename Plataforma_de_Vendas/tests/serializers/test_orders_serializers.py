import pytest
from Orders.serializers import OrderSerializer


@pytest.mark.django_db
class TestOrderSerializer:
    def test_invalid_user_and_store(self):
        """Test that the serializer raises validation errors
        with the correct ID when user or store do not exist."""
        invalid_user_id = "99999"
        invalid_store_id = "55555"

        data = {
            "user": invalid_user_id,
            "store": invalid_store_id,
            "status": "pending",
        }

        serializer = OrderSerializer(data=data)

        assert not serializer.is_valid()
        assert serializer.errors["user"] == f"User with ID {invalid_user_id} does not exist."
        assert serializer.errors["store"] == f"Store with ID {invalid_store_id} does not exist."

    def test_valid_user_and_store(self, customer_fixture, store_fixture):
        """Test that the serializer is valid with valid user and store IDs."""
        customer_user, _ = customer_fixture
        store = store_fixture

        data = {
            "user": customer_user.id,
            "store": store.id,
            "status": "PENDING",
            "total": 100.00,
        }

        serializer = OrderSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["user"] == customer_user
        assert serializer.validated_data["store"] == store
