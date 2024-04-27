from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def run_validation(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        account_type = attrs.get('account_type')
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})
        if CustomUser.objects.filter(username=username, email=email).exists():
            raise serializers.ValidationError({"username": "Username already exists", "email": "Email already exists"})
        elif CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        elif CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        
        if account_type not in ['customer', 'seller', 'admin']:
            raise serializers.ValidationError({"account_type": "Invalid account type"})
        
        return attrs