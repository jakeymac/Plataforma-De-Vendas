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
from .serializers import CustomUserSerializer, ExistingUserSerializer
from Stores.models import Store

import json

import logging

logger = logging.getLogger('plataforma_de_vendas')

@swagger_auto_schema(method='GET',
    operation_description="Get all users",
    responses={200: CustomUserSerializer(many=True)})
@api_view(['GET'])
def get_users_endpoint(request):
    if request.user.is_authenticated and request.user.account_type == 'admin':
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
    if request.user.is_authenticated and request.user.account_type == 'admin':
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get all customers",
    responses={200: CustomUserSerializer(many=True)})
@api_view(['GET'])
def get_customers_endpoint(request):
    if request.user.is_authenticated and request.user.account_type == 'admin':
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
    if request.user.is_authenticated and request.user.account_type == 'admin':
        admins = CustomUser.objects.filter(account_type='admin')
        serializer = CustomUserSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

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
    user = request.user
    if request.user.is_authenticated and request.user.id == int(data.get("id")):
        serializer = ExistingUserSerializer(instance=user, data=data)
        if serializer.is_valid():
            serializer.save()
            response = {"message": "User updated"}
            response["user_info"] = serializer.data
            return Response(response, status.HTTP_200_OK)
        response = {"message": "User not updated"}
        response["errors"] = serializer.errors
        return Response(response, status.HTTP_400_BAD_REQUEST)
    return Response({"message": "You are not authorized to make changes to this account"}, status.HTTP_401_UNAUTHORIZED)

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
    logger.info("logging in endpoint...")
    try:
        data = request.data
        username = data.get("username")
        password = data.get("password")
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Logged in"}, status.HTTP_200_OK)
    except Exception as e:
        logger.warning(f"Error logging in: {e}")
        return Response({"message": e}, status.HTTP_401_UNAUTHORIZED)
    return Response({"message": "Username or password is incorrect"}, status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def logout_endpoint(request):
    logout(request)
    return Response({"message": "Logged out"}, status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties = {
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="User's first name"),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="User's last name"),
            'date_of_birth': openapi.Schema(type=openapi.TYPE_STRING, description="User's date of birth"),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description="User's phone number"),
            'address': openapi.Schema(type=openapi.TYPE_STRING, description="User's address"),
            'address_line_two': openapi.Schema(type=openapi.TYPE_STRING, description="User's address line two"),
            'city': openapi.Schema(type=openapi.TYPE_STRING, description="User's city"),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description="User's state"),
            'zip_code': openapi.Schema(type=openapi.TYPE_STRING, description="User's zip code"),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description="User's country"),
            'profile_picture': openapi.Schema(type=openapi.TYPE_FILE, description="User's profile picture"),
            'account_type': openapi.Schema(type=openapi.TYPE_STRING, description="User's account type")
        }
    )
)
@api_view(['POST'])
def register_account_endpoint(request):
    data = request.data
    if data.get("account_type") == "customer":
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(data.get("password"))
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "Incorrect endpoint for registering admin accounts and sellers"}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties = {
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
        }
    )
)
@api_view(['POST'])
def check_username_availability_endpoint(request):
    data = request.data
    if data.get("username") in CustomUser.objects.all().values_list('username', flat=True):
        return Response({"is_available": False}, status=status.HTTP_200_OK)
    return Response({"is_available": True}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties = {
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
        }
    )
)
@api_view(['POST'])
def check_email_availability_endpoint(request):
    data = request.data
    if data.get("email") in CustomUser.objects.all().values_list('email', flat=True):
        return Response({"is_available": False}, status=status.HTTP_200_OK)
    return Response({"is_available": True}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties = {
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="User's ID"),
            'profile_picture': openapi.Schema(type=openapi.TYPE_FILE, description="User's profile picture"),
        }
    )
)
@api_view(['PUT'])
def update_profile_picture_endpoint(request):
    data = request.data
    if request.user.is_authenticated and request.user.id == int(data.get("id")):
        if request.user.profile_picture:
            request.user.profile_picture.delete()
        
        request.user.profile_picture = data.get("profile_picture")
        request.user.save()
        return Response({"message": "Profile picture updated"}, status=status.HTTP_200_OK)
    return Response({"message": "You are not logged in"}, status=status.HTTP_401_UNAUTHORIZED)
    l