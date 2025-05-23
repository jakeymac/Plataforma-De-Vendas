# API endpoints for accounts
import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .serializers import CustomUserSerializer, ExistingUserSerializer

logger = logging.getLogger("plataforma_de_vendas")


@swagger_auto_schema(
    method="GET",
    operation_description="Get all users",
    responses={200: CustomUserSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users_endpoint(request):
    if request.user.groups.filter(name="Admins").exists():
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method="GET",
    operation_description="Get a user by ID",
    responses={200: CustomUserSerializer()},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_endpoint(request, user_id):
    if request.user.groups.filter(name="Admins").exists():
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = CustomUserSerializer(user, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    # TODO may want to look at this, but for now this is the behavior of this endpoint
    elif request.user.id == user_id:
        user = CustomUser.objects.get(id=user_id)
        serializer = CustomUserSerializer(user, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method="GET",
    operation_description="Get all customers",
    responses={200: CustomUserSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customers_endpoint(request):
    if request.user.groups.filter(name="Admins").exists():
        customer_group = Group.objects.get(name="Customers")
        customers = CustomUser.objects.filter(groups=customer_group)
        serializer = CustomUserSerializer(customers, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method="GET",
    operation_description="Get all admins",
    responses={200: CustomUserSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_admins_endpoint(request):
    if request.user.groups.filter(name="Admins").exists():
        admin_group = Group.objects.get(name="Admins")
        admins = CustomUser.objects.filter(groups=admin_group)
        serializer = CustomUserSerializer(admins, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


# TODO add an endpoint for getting all sellers

# TODO add an endpoint to create a new account
# MUST USE SERIALIZER


# TODO add schema info here.
@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="User's first name")
        },
    ),
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def edit_user_endpoint(request):
    data = request.data
    if request.user.id == str(data.get("id")) or request.user.groups.filter(name="Admins").exists():
        try:
            user = CustomUser.objects.get(id=data.get("id"))
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status.HTTP_404_NOT_FOUND)
        serializer = ExistingUserSerializer(instance=user, data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            response = {"message": "User updated"}
            response["user_info"] = serializer.data
            return Response(response, status.HTTP_200_OK)
        response = {"message": "User not updated"}
        response["errors"] = serializer.errors
        return Response(response, status.HTTP_400_BAD_REQUEST)
    return Response(
        {"message": "You are not authorized to make changes to this account"},
        status.HTTP_401_UNAUTHORIZED,
    )


@swagger_auto_schema(
    method="get",
    operation_description="Get all users",
    responses={200: CustomUserSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user_info_endpoint(request):
    # TODO make this more secure (remove password, etc from response body)
    serializer = CustomUserSerializer(request.user, context={"request": request})
    return Response(serializer.data, status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
        },
    ),
)
@api_view(["POST", "GET"])  # TODO remove GET method
def login_endpoint(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")

    if username is None and password is None:
        return Response(
            {"message": "Username and password are required"}, status.HTTP_400_BAD_REQUEST
        )

    if username is None:
        return Response({"message": "Username is required"}, status.HTTP_400_BAD_REQUEST)

    if password is None:
        return Response({"message": "Password is required"}, status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({"message": "Logged in"}, status.HTTP_200_OK)
    else:
        return Response(
            {"message": "Username or password is incorrect"},
            status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["GET"])
def logout_endpoint(request):
    logout(request)
    return Response({"message": "Logged out"}, status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
            "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="User's first name"),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING, description="User's last name"),
            "date_of_birth": openapi.Schema(
                type=openapi.TYPE_STRING, description="User's date of birth"
            ),
            "phone_number": openapi.Schema(
                type=openapi.TYPE_STRING, description="User's phone number"
            ),
            "address": openapi.Schema(type=openapi.TYPE_STRING, description="User's address"),
            "address_line_two": openapi.Schema(
                type=openapi.TYPE_STRING, description="User's address line two"
            ),
            "city": openapi.Schema(type=openapi.TYPE_STRING, description="User's city"),
            "state": openapi.Schema(type=openapi.TYPE_STRING, description="User's state"),
            "zip_code": openapi.Schema(type=openapi.TYPE_STRING, description="User's zip code"),
            "country": openapi.Schema(type=openapi.TYPE_STRING, description="User's country"),
            "profile_picture": openapi.Schema(
                type=openapi.TYPE_FILE, description="User's profile picture"
            ),
            "account_type": openapi.Schema(
                type=openapi.TYPE_STRING, description="User's account type"
            ),
        },
    ),
)
@api_view(["POST"])
def register_customer_account_endpoint(request):
    data = request.data
    # TODO may want to remove this check, just have all accounts sent to this endpoint be customers
    if data.get("account_type") == "customer":
        serializer = CustomUserSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(data.get("password"))
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {"message": ("Incorrect endpoint for registering admin accounts and sellers")},
            status=status.HTTP_400_BAD_REQUEST,
        )


# TODO add an endpoint for adding new sellers to a store that's secure


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
        },
    ),
)
@api_view(["POST"])
def check_username_availability_endpoint(request):
    # TODO this may not be entirely secure as it is possible to check all usernames
    data = request.data
    if data.get("username") in CustomUser.objects.all().values_list("username", flat=True):
        return Response({"is_available": False}, status=status.HTTP_200_OK)
    return Response({"is_available": True}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
        },
    ),
)
@api_view(["POST"])
def check_email_availability_endpoint(request):
    # TODO this may not be entirely secure as it is possible to check all emails

    # TODO could update this endpoint to check if the provided email
    # is even an actual email address in the first place
    data = request.data
    if data.get("email") in CustomUser.objects.all().values_list("email", flat=True):
        return Response({"is_available": False}, status=status.HTTP_200_OK)
    return Response({"is_available": True}, status=status.HTTP_200_OK)


# TODO update this endpoint to use s3 bucket and upload file
@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="User's ID"),
            "profile_picture": openapi.Schema(
                type=openapi.TYPE_FILE, description="User's profile picture"
            ),
        },
    ),
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile_picture_endpoint(request):
    data = request.data
    new_profile_picture = request.FILES.get("profile_picture")

    if request.user.id == str(data.get("id")) or request.user.groups.filter(name="Admins").exists():
        user = CustomUser.objects.get(id=data.get("id"))
        if user.profile_picture and new_profile_picture:
            user.profile_picture.delete()

        if new_profile_picture:
            user.profile_picture = new_profile_picture
            user.save()
            return Response({"message": "Profile picture updated."}, status=status.HTTP_200_OK)
        return Response(
            {"message": "No profile picture provided."}, status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {"message": "You are not authorized to update this account's profile picture."},
        status=status.HTTP_401_UNAUTHORIZED,
    )


# TODO convert this view to an endpoint using s3 bucket:
# @login_required
# def retrieve_profile_picture(request, username):
#     if request.user.is_authenticated:
#         if (
#             request.user.groups.filter(name="Admins").exists()
#             or request.user.username == username
#         ):
#             user = CustomUser.objects.get(username=username)
#             if user.profile_picture:
#                 file_path = os.path.join(
#                     settings.MEDIA_ROOT, "profile_pictures", user.profile_picture
#                 )
#                 if os.path.exists(file_path):
#                     with open(file_path, "rb") as file:
#                         response = HttpResponse(file.read(), content_type="image")
#                         response["Content-Disposition"] = (
#                             "inline; filename=" + os.path.basename(file_path)
#                         )
#                         response["status"] = 200
#                         return response
#                 return HttpResponse(
#                     {"error": "Issue retreiving profile picture."}, status=404
#                 )
#             return HttpResponse({"error": "No profile picture specified"}, status=400)
#     return HttpResponse({"error": "Unauthorized"}, status=400)
