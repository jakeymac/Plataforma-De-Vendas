#API endpoints for stores
from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Store
from Accounts.serializers import CustomUserSerializer
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

            if request.user.account_type == 'admin' or request.user.id == store.owner.id:
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

 
#Helper function for register store endpoint
def parse_store_registration_data(request_data, request_files):
    account_data = {
        "username": request_data.get("username"),
        "password": request_data.get("password"),
        "email": request_data.get("email"),
        "first_name": request_data.get("first_name"),
        "last_name": request_data.get("last_name"),
        "date_of_birth": request_data.get("date_of_birth"),
        "phone_number": request_data.get("phone_number"),
        "address": request_data.get("address"),
        "address_line_two": request_data.get("address_line_two"),
        "city": request_data.get("city"),
        "state": request_data.get("state"),
        "country": request_data.get("country"),
        "zip_code": request_data.get("zip_code"),
        "profile_picture": request_files.get("profile_picture")
    }

    # Format the date_of_birth to 'YYYY-MM-DD' for saving to database
    if account_data["date_of_birth"]:
        account_data["date_of_birth"] = account_data["date_of_birth"].strftime('%Y-%m-%d')
    else:
        account_data["date_of_birth"] = None

    store_data = {
        "store_name": request_data.get("store_name"),
        "store_description": request_data.get("store_description"),
        "store_url": request_data.get("store_url"),
        "store_logo": request_files.get("store_logo")
    }
    return account_data, store_data

@api_view(['POST'])
def register_store_endpoint(request):
    account_data, store_data = parse_store_registration_data(request.POST, request.FILES)

    account_data["account_type"] = "seller"
    account_serializer = CustomUserSerializer(data=account_data)
    store_serializer = StoreSerializer(data=store_data)
    account_data_is_valid = account_serializer.is_valid()
    store_data_is_valid = store_serializer.is_valid()
    if store_data_is_valid and account_data_is_valid:
        try:
            with transaction.atomic():
                account = account_serializer.save()
                account.set_password(account_data["password"])
                account.save()

                store = store_serializer.save()
                account.store = store
                account.save()

            return Response({"message": "Store created successfully"}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"message": "An error occurred", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        errors = {}
        if account_serializer.errors:
            errors["account_errors"] = account_serializer.errors
        if store_serializer.errors:
            errors["store_errors"] = store_serializer.errors
        return Response({"message": "Store not created", "errors": errors}, status=status.HTTP_200_OK)
        