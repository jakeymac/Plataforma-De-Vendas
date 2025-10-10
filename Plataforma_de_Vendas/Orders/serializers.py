from Accounts.models import CustomUser
from rest_framework import serializers
from Stores.models import Store

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())

    user_username = serializers.CharField(source="user.username", read_only=True)
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    store_name = serializers.CharField(source="store.store_name", read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

    def to_internal_value(self, data):
        """Override this method to include the provided ID in error messages."""
        errors = {}

        # Extract user and store IDs from the incoming data
        user_id = data.get("user")
        store_id = data.get("store")

        # Validate user
        if user_id and not CustomUser.objects.filter(id=user_id).exists():
            errors["user"] = f"User with ID {user_id} does not exist."

        # Validate store
        if store_id and not Store.objects.filter(id=store_id).exists():
            errors["store"] = f"Store with ID {store_id} does not exist."

        if errors:
            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)
