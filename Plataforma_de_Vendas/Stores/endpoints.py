# API endpoints for stores
from datetime import datetime

from Accounts.serializers import CustomUserSerializer
from django.db import transaction
from django.contrib.auth.models import Group
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .models import Store
from .serializers import StoreSerializer


# Helper function for register store endpoint
def parse_store_registration_data(request_data, request_files):
    account_data = {
        "username": request_data.get("username"),
        "password": request_data.get("password"),
        "email": request_data.get("email"),
        "first_name": request_data.get("first_name"),
        "last_name": request_data.get("last_name"),
        "date_of_birth": request_data.get("date_of_birth"),
        "phone_number": request_data.get("phone_number"),
        "country_phone_number_code": request_data.get("country_phone_number_code"),
        "address": request_data.get("address"),
        "address_line_two": request_data.get("address_line_two"),
        "city": request_data.get("city"),
        "state": request_data.get("state"),
        "country": request_data.get("country"),
        "zip_code": request_data.get("zip_code"),
        "profile_picture": request_files.get("profile_picture"),
    }

    # Format the date_of_birth to 'YYYY-MM-DD' for saving to database
    if account_data["date_of_birth"]:
        if isinstance(account_data["date_of_birth"], str):
            account_data["date_of_birth"] = datetime.strptime(
                account_data["date_of_birth"], "%Y-%m-%d"
            )
        account_data["date_of_birth"] = account_data["date_of_birth"].strftime("%Y-%m-%d")
    else:
        account_data["date_of_birth"] = None

    store_data = {
        "store_name": request_data.get("store_name"),
        "store_description": request_data.get("store_description"),
        "store_url": request_data.get("store_url"),
        "store_logo": request_files.get("store_logo"),
    }
    return account_data, store_data


@swagger_auto_schema(
    method="get",
    responses={200: "OK"},
    description="Get a store by ID",
)
@api_view(["GET"])
def get_store_endpoint(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        serializer = StoreSerializer(store)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Store.DoesNotExist:
        return Response(
            {"message": f"Store not found with the id {store_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(
    method="get",
    responses={200: "OK"},
    description="Get all stores",
)
@api_view(["GET"])
def get_stores_endpoint(request):
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["id"],
        properties={
            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Store id"),
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Store name"),
            "description": openapi.Schema(
                type=openapi.TYPE_STRING, description="Store description"
            ),
        },
    ),
    responses={200: "Updated"},
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_store_endpoint(request):
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
    ):
        data = request.data
        store_id = data.get("id")
        try:
            store = Store.objects.get(id=store_id)

            if (
                not request.user.groups.filter(name="Admins").exists()
                and request.user.store.id != store.id
            ):
                return Response(
                    {"message": "You are not authorized to update this store"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = StoreSerializer(store, data=data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data.copy()
                response_data["message"] = "Store updated successfully"
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Store.DoesNotExist:
            return Response(
                {"message": f"Store not found with the id {store_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

    return Response(
        {"message": "You are not authorized to update stores"},
        status=status.HTTP_403_FORBIDDEN,
    )


@api_view(["POST"])
def register_store_endpoint(request):
    account_data, store_data = parse_store_registration_data(request.POST, request.FILES)

    # account_data["account_type"] = "seller" # TODO delete this later
    account_serializer = CustomUserSerializer(data=account_data, context={"request": request})
    store_serializer = StoreSerializer(data=store_data)
    account_data_is_valid = account_serializer.is_valid()
    store_data_is_valid = store_serializer.is_valid()
    if store_data_is_valid and account_data_is_valid:
        with transaction.atomic():
            account = account_serializer.save()
            account.set_password(account_data["password"])
            account.groups.add(Group.objects.get(name="Sellers"))

            # TODO add permissions to this account as owner of the store
            account.save()

            store = store_serializer.save()
            account.store = store
            account.save()

        return Response(
            {"message": "Store created successfully"},
            status=status.HTTP_201_CREATED,
        )

    else:
        errors = {}
        if account_serializer.errors:
            errors["account_errors"] = account_serializer.errors
        if store_serializer.errors:
            errors["store_errors"] = store_serializer.errors
        return Response(
            {"message": "Store not created", "errors": errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
