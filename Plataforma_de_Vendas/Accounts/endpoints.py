#API endpoints for accounts
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout

from django.db.models import Q
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CustomUser
from .serializers import CustomUserSerializer
from Stores.models import Store

import json

@swagger_auto_schema(method='GET',
    operation_description="Get all users",
    responses={200: CustomUserSerializer(many=True)})
@api_view(['GET'])
def get_users_endpoint(request):
    if request.user.is_authenticated and request.user.is_superuser:
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get a user by ID",
    responses={200: CustomUserSerializer()})
@api_view(['GET'])
def get_user_endpoint(request, user_id):
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get sellers by store ID",
    responses={200: CustomUserSerializer(many=True)})
@api_view(['GET'])
def get_sellers_by_store_endpoint(request, store_id):
    if request.user.is_authenticated and request.user.is_superuser:
        sellers = CustomUser.objects.filter(store_id=store_id, account_type='seller')
        serializer = CustomUserSerializer(sellers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get all sellers",
    responses={200: CustomUserSerializer(many=True)})
@api_view(['GET'])
def get_sellers_endpoint(request):
    if request.user.is_authenticated and request.user.is_superuser:
        sellers = CustomUser.objects.filter(account_type='seller')
        serializer = CustomUserSerializer(sellers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get all customers",
    responses={200: CustomUserSerializer(many=True)})
@api_view(['GET'])
def get_customers_endpoint(request):
    if request.user.is_authenticated and request.user.is_superuser:
        customers = CustomUser.objects.filter(account_type='customer')
        serializer = CustomUserSerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get all admins",
    responses={200: CustomUserSerializer(many=True)})
@api_view(['GET'])
def get_admins_endpoint(request):
    if request.user.is_authenticated and request.user.is_superuser:
        admins = CustomUser.objects.filter(account_type='admin')
        serializer = CustomUserSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name':openapi.Schema(type=openapi.TYPE_STRING, description="User first name"),
            'last_name':openapi.Schema(type=openapi.TYPE_STRING, description="User last name"),
            'account_type':openapi.Schema(type=openapi.TYPE_STRING, description="User account type"),
        }
    ),
    responses={201:'Created'}
)
@api_view(['POST'])
def add_user_endpoint(request):
    data = request.data
    if data.get("account_type") != "admin":
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        if request.user.is_authenticated and request.user.is_superuser:
            serializer = CustomUserSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "You do not have permission to create admin accounts."}, status.HTTP_401_UNAUTHORIZED)

#TODO add schema info here.
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="User's first name")
        }
    )
)
@api_view(['PUT'])
def edit_user_endpoint(request):
    data = request.data
    if request.user.is_authenticated and request.user.id == data.id:
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    return Response({"messages": "You are not authorized to make changes to this account"}, status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(
    method='get',
    operation_description="Get all users",
    responses={200: CustomUserSerializer(many=True)}
)
@api_view(['GET'])
def get_current_user_info_endpoint(request):
    # TODO make this more secure (remove password, etc from response body)
    if request.user.is_authenticated:
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status.HTTP_200_OK)
    return Response({"message": "You are not logged in"}, status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="User's password")
        }
    )
)
@api_view(['POST','GET'])
def login_endpoint(request):
    import pdb
    pdb.set_trace()
    try:
        data = request.data
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user is not None:
            login(request, user)
            return Response({"message": "Logged in"}, status.HTTP_200_OK)
    except:
        pass
    return Response({"message": "Invalid credentials"}, status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def logout_endpoint(request):
    logout(request)
    return Response({"message": "Logged out"}, status.HTTP_200_OK)

