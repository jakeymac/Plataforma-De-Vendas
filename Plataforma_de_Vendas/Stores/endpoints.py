#API endpoints for stores
from django.contrib.auth import authenticate


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Store
from .serializers import StoreSerializer

import json


@swagger_auto_schema(
    method='get',
    responses={200: 'OK'},
    description='Get all stores or a specific store by id'
)
@api_view(['GET'])
def get_stores_endpoint(request,store_id=None):
    if store_id is not None:
        try:
            store = Store.objects.get(id=store_id)
            serializer = StoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({"message": f"Store not found with the id {store_id}"}, status=status.HTTP_404_NOT_FOUND)
    else:   
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'description'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Product name'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Product description'),
            # Add other fields as needed
        }
    ),
    responses={200: 'Created'}
)
@api_view(['POST'])
def add_store_endpoint(request):
    data = request.data
    serializer = StoreSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Store id'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Store name'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Store description'),
        }
    ),
    responses={200: 'Updated'}
)
@api_view(['PUT'])
def update_store_endpoint(request):
    data = request.data
    store_id = data.get('id')
    try:
        store = Store.objects.get(id=store_id)
        if request.user.is_authenticated:

            if request.user.is_superuser or request.user.id == store.owner.id:
                serializer = StoreSerializer(store, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "You are not authorized to update this store"}, status=status.HTTP_401_UNAUTHORIZED)

    except Store.DoesNotExist:
        return Response({"message": f"Store not found with the id {store_id}"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StoreSerializer(store, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
