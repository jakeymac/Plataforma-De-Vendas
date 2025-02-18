import re

from django.contrib.auth.models import Group
from rest_framework import serializers
from Stores.models import Store

from .models import CustomUser

# Account types for the CustomUser model to add to groups
account_types = {
    "admin": "Admins",
    "seller": "Sellers",
    "customer": "Customers",
}


def is_phone_number_valid(phone_number, country_code):
    # TODO have this check for correct placement of the hyphens, not just number of hyphens
    hyphen_count = phone_number.count("-")
    if str(country_code) == "55" and hyphen_count > 2:
        return False

    if str(country_code) == "1" and hyphen_count > 3:
        return False

    numbers = re.sub(r"\D", "", phone_number)
    # Brasil
    if str(country_code) == "55":
        return len(numbers) in [10, 11]

    # USA
    elif str(country_code) == "1":
        return len(numbers) == 10


def is_country_code_valid(country_code):
    return str(country_code) in ["1", "55"]


def format_phone_number(country, phone_number):
    numbers = re.sub(r"\D", "", phone_number)
    # Brasil
    if str(country) == "55":
        if len(numbers) == 10:
            return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
        elif len(numbers) == 11:
            return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"

    # USA
    elif str(country) == "1":
        return f"({numbers[:3]}) {numbers[3:6]}-{numbers[6:]}"


class CustomUserSerializer(serializers.ModelSerializer):
    account_type = serializers.CharField(write_only=True, required=False)

    # This allows for a custom error message for non-existent store ids
    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        required=False,
        error_messages={"does_not_exist": "Store does not exist"},
    )

    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate(self, data):
        errors = {}
        request = self.context.get("request")
        # TODO may change this to not specifically need a request user
        if request and request.user:
            requesting_user = request.user
        else:
            raise serializers.ValidationError("Request context is required for security purposes")
            return data

        if data.get("account_type") and data.get("account_type") not in account_types:
            errors["account_type"] = "Invalid account type"

        if (
            data.get("account_type") == "admin"
            and not requesting_user.groups.filter(name="Admins").exists()
        ):
            raise serializers.ValidationError("Only admins can create admin accounts")
            return data

        if len(data.get("password")) < 8:
            errors["password"] = "Password must have at least 8 characters"

        pattern = r"^\d{5}(-\d{4})?$"
        if data.get("zip_code") and not re.match(pattern, data.get("zip_code")):
            errors["zip_code"] = "Invalid zip code"

        if data.get("phone_number") and data.get("country_phone_number_code"):
            if not is_country_code_valid(data.get("country_phone_number_code")):
                errors["country_phone_number_code"] = "Invalid country code"

            if not is_phone_number_valid(
                data.get("phone_number"), data.get("country_phone_number_code")
            ):
                errors["phone_number"] = "Invalid phone number"

        if data.get("account_type") == "seller":
            if not data.get("store"):
                errors["store"] = "Seller account must have a store"

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        if validated_data.get("country_phone_number_code") and validated_data.get("phone_number"):
            validated_data["phone_number"] = format_phone_number(
                validated_data.get("country_phone_number_code"),
                validated_data.get("phone_number"),
            )
        password = validated_data.pop("password", None)
        account_type = validated_data.pop("account_type", None)
        user = super().create(validated_data)

        if account_type:
            group = Group.objects.get(name=account_types[account_type])
            user.groups.add(group)

        if password:
            user.set_password(password)

        user.save()

        return user


class ExistingUserSerializer(CustomUserSerializer):
    """Used for validating and updating existing users."""

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate(self, data):
        errors = {}
        request = self.context.get("request")
        if request and request.user:
            requesting_user = request.user
        else:
            raise serializers.ValidationError("Request context is required for security purposes")
            return data

        if (
            data.get("account_type") == "admin"
            and not requesting_user.groups.filter(name="Admins").exists()
        ):
            raise serializers.ValidationError("Only admins can create admin accounts")
            return data

        if self.instance:
            if data.get("password") and len(data.get("password")) < 8:
                errors["password"] = "Password must have at least 8 characters"

            pattern = r"^\d{5}(-\d{4})?$"
            if data.get("zip_code") and not re.match(pattern, data.get("zip_code")):
                errors["zip_code"] = "Invalid zip code"

            if data.get("phone_number") and data.get("country_phone_number_code"):
                if not is_phone_number_valid(
                    data.get("phone_number"), data.get("country_phone_number_code")
                ):
                    errors["phone_number"] = "Invalid phone number"

            if errors:
                raise serializers.ValidationError(errors)

            return data

        else:
            raise serializers.ValidationError("Serializer only to be used for existing users")

    def update(self, instance, validated_data):
        if validated_data.get("country_phone_number_code") and validated_data.get("phone_number"):
            validated_data["phone_number"] = format_phone_number(
                validated_data.get("country_phone_number_code"),
                validated_data.get("phone_number"),
            )

        if validated_data.get("password", None):
            password = validated_data.pop("password")
            instance.set_password(password)

        account_type = validated_data.pop("account_type", None)

        if account_type:
            group = Group.objects.get(name=account_types[account_type])
            instance.groups.add(group)

        return super().update(instance, validated_data)
