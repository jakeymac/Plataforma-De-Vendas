from rest_framework import serializers
from .models import CustomUser

import re

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def validate(self, data):
        errors = {}
        if data['account_type'] == 'admin' and not self.instance.is_superuser:
            raise serializers.ValidationError('Only superusers can create admin accounts')
        return data

        if data['username'] in CustomUser.objects.all().values_list('username', flat=True):
            errors["username"] = "Username already exists"

        if data['email'] in CustomUser.objects.all().values_list('email', flat=True):
            errors["email"] = "Email already exists"

        if len(data['password']) < 8:
            errors["password"] = "Password must have at least 8 characters"

        breakpoint()
        pattern = r'^\d{5}(-\d{4})?$'
        if not re.match(pattern, data['zip_code']):
            errors["zip_code"] = "Invalid zip code"

        if errors:
            raise serializers.ValidationError(errors)
        
        return data

        