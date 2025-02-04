from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"

    def run_validation(self, attrs):
        store_name = attrs.get("store_name")
        store_url = attrs.get("store_url")

        errors = {}
        if Store.objects.filter(store_name=store_name).exists():
            errors["store_name"] = "Store with this name already exists"
        if Store.objects.filter(store_url=store_url).exists():
            errors["store_url"] = "Store with this url already exists"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
