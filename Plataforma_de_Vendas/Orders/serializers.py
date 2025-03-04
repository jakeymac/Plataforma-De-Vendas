from Accounts.models import CustomUser
from rest_framework import serializers
from Stores.models import Store

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())

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
