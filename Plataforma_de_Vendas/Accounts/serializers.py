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

        if self.instance:
            if self.instance.username != data['username'] and CustomUser.objects.filter(username=data['username']).exists():
                errors['username'] = 'Username already exists'
            if self.instance.email != data['email'] and CustomUser.objectsfilter(email=data['email']).exists():
                errors["email"] = "Email already exists"
        else:
            if CustomUser.objects.filter(username=data['username']).exists():
                errors['username'] = 'Username already exists'

            if CustomUser.objects.filter(email=data['email']).exists():
                errors["email"] = "Email already exists"

        if len(data['password']) < 8:
            errors["password"] = "Password must have at least 8 characters"
            
        pattern = r'^\d{5}(-\d{4})?$'
        if data['zip_code'] and not re.match(pattern, data['zip_code']):
            errors["zip_code"] = "Invalid zip code"

        if not self.is_phone_number_valid(data['phone_number'], data['country_phone_number_code']):
            errors["phone_number"] = "Invalid phone number"

        if errors:
            raise serializers.ValidationError(errors)
        
        return data

    def is_phone_number_valid(self, phone_number, country_code):
        numbers = re.sub(r'\D', '', phone_number)
        # Brasil
        if country_code == "55": 
            return len(numbers) in [10, 11]

        # USA  
        elif country_code == "1":
            return len(numbers) == 10

    def format_phone_number(self, country, phone_number):
        numbers = re.sub(r'\D', '', phone_number)
        # Brasil
        if str(country) == "55":
            if len(numbers) == 10:
                return f"({numbers[:2]}) {numbers[2:6]}-{numbers[6:]}"
            elif len(numbers) == 11:
                return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"

        # USA
        elif str(country) == "1":
            return f"+{country} ({numbers[:3]}) {numbers[3:6]}-{numbers[6:]}"

    def create(self, validated_data):
        validated_data['phone_number'] = self.format_phone_number(validated_data['country_phone_number_code'], validated_data['phone_number'])
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
        
        user.save()

        return user

    def update(self, instance, validated_data):
        validated_data['phone_number'] = self.format_phone_number(validated_data['country_phone_number_code'], validated_data['phone_number'])
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)