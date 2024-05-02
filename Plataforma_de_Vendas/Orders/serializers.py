from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def run_validation(self, attrs):
        status = attrs.get('status')
        if status not in ['PENDING', 'IN_PROGRESS', 'DONE']:
            raise serializers.ValidationError({"status": "Invalid status"})
        return attrs