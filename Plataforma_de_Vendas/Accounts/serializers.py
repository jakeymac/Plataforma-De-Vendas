import re

from rest_framework import serializers
from Stores.models import Store

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate(self, data):
        errors = {}

        if (
            data.get("account_type") == "admin"
            and not self.instance.groups.filter(name="Admins").exists()
        ):
            raise serializers.ValidationError("Only admins can create admin accounts")
            return data

        if self.instance:
            if (
                self.instance.username != data.get("username")
                and CustomUser.objects.filter(username=data.get("username")).exists()
            ):
                errors["username"] = "Username already exists"
            if (
                self.instance.email != data.get("email")
                and CustomUser.objectsfilter(email=data.get("email")).exists()
            ):
                errors["email"] = "Email already exists"
        else:
            if CustomUser.objects.filter(username=data.get("username")).exists():
                errors["username"] = "Username already exists"

            if CustomUser.objects.filter(email=data.get("email")).exists():
                errors["email"] = "Email already exists"

        if len(data.get("password")) < 8:
            errors["password"] = "Password must have at least 8 characters"

        pattern = r"^\d{5}(-\d{4})?$"
        if data.get("zip_code") and not re.match(pattern, data.get("zip_code")):
            errors["zip_code"] = "Invalid zip code"

        print("Testing output...")
        print("Phone number: ", data.get("phone_number"))
        print("Country code: ", data.get("country_phone_number_code"))

        if data.get("phone_number") and data.get("country_phone_number_code"):
            if not self.is_phone_number_valid(
                data.get("phone_number"), data.get("country_phone_number_code")
            ):
                errors["phone_number"] = "Invalid phone number"
        

        if data.get("account_type") == "seller":
            if not data.get("store"):
                errors["store"] = "Seller account must have a store"
            else:
                if not Store.objects.filter(id=data.get("store")).exists():
                    errors["store_id"] = "Store does not exist"

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def is_phone_number_valid(self, phone_number, country_code):
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

    def format_phone_number(self, country, phone_number):
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

    def create(self, validated_data):
        if validated_data.get("country_phone_number_code") and validated_data.get("phone_number"):
            validated_data["phone_number"] = self.format_phone_number(
                validated_data.get("country_phone_number_code"),
                validated_data.get("phone_number"),
            )
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)

        user.save()

        return user

    def update(self, instance, validated_data):
        if validated_data.get("country_phone_number_code") and validated_data.get("phone_number"):
            validated_data["phone_number"] = self.format_phone_number(
                validated_data.get("country_phone_number_code"),
                validated_data.get("phone_number"),
            )
        
        if validated_data.get("password", None):
            password = validated_data.pop("password")
            instance.set_password(password)

        return super().update(instance, validated_data)


class ExistingUserSerializer(CustomUserSerializer):
    """Used for validating and updating existing users."""

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = "__all__"

    def validate(self, data):
        errors = {}
        if self.instance:
            if (
                self.instance.username != data.get("username")
                and CustomUser.objects.filter(username=data.get("username")).exists()
            ):
                errors["username"] = "Username already exists"
            if (
                self.instance.email != data.get("email")
                and CustomUser.objects.filter(email=data.get("email")).exists()
            ):
                errors["email"] = "Email already exists"
            if data.get("password") and len(data.get("password")) < 8:
                errors["password"] = "Password must have at least 8 characters"

            pattern = r"^\d{5}(-\d{4})?$"
            if data.get("zip_code") and not re.match(pattern, data.get("zip_code")):
                errors["zip_code"] = "Invalid zip code"

            if data.get("phone_number") and data.get("country_phone_number_code"):
                if not self.is_phone_number_valid(
                    data.get("phone_number"), data.get("country_phone_number_code")
                ):
                    errors["phone_number"] = "Invalid phone number"


            if errors:
                raise serializers.ValidationError(errors)

            return data

        else:
            raise serializers.ValidationError("Serializer only to be used for existing users")
