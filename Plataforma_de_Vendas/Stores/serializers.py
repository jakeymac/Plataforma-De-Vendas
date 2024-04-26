from rest_framework import serializers
from .models import Store

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
    
    def run_validation(self, attrs):
        store_name = attrs.get('name')
        url = attrs.get('url')

        errors = []
        if Store.objects.filter(name=store_name).exists():
            errors.append({"name": "Store with this name already exists"})
        if Store.objects.filter(url=url).exists():
            errors.append({"store": "Store with this url already exists"})

        if errors:
            if len(errors) == 1:
                raise serializers.ValidationError(errors[0])
            else:
                raise serializers.ValidationError({"various": "A store already exists with that name and url"})

        return attrs
        
        