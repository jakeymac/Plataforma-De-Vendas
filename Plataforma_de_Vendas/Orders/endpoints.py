# API endpoints for orders

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from .models import Order
from .serializers import OrderSerializer
from Stores.models import Store
from Accounts.models import Customuser


@swagger_auto_schema(
    method="GET",
    operation_description="Get all orders",
    responses={200: OrderSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders_endpoint(request):
    if request.user.groups.filter(name="Admins").exists():
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method="GET",
    operation_description="Get an order by ID",
    responses={200: OrderSerializer()},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_endpoint(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        if (
            request.user.groups.filter(name="Admins").exists()
            or (
                request.user.groups.filter(name="Sellers")
                and order.store == request.user.store
            )
            or order.user == request.user
        ):
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"message": "You are not authorized to view this order"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    except Order.DoesNotExist:
        return Response(
            {"message": f"Order not found with the id {order_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


# TODO add an endpoint for a seller to get all their orders from a specific user


@swagger_auto_schema(
    method="GET",
    operation_description="Get orders by user ID",
    responses={200: OrderSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders_by_user_endpoint(request, user_id):
    if request.user.groups.filter(name="Admins").exists() or request.user.id == user_id:
        try:
            user_object = CustomUser.objects.get(id=user_id)
            orders = Order.objects.filter(user=user_object)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response(
                {"message": f"User not found with the id {user_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

    return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method="GET",
    operation_description="Get orders by store ID",
    responses={200: OrderSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders_by_store_endpoint(request, store_id):
    # TODO add a check to see if the user is a seller and 
    # if they have permissions to view orders ( MAYBE )
    if request.user.groups.filter(name="Admins").exists() or (
        request.user.groups.filter(name="Sellers").exists()
        and request.user.store.id == store_id
    ):
        try:
            store = Store.objects.get(id=store_id)
            orders = Order.objects.filter(store=store)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response(
                {"message": f"Store not found with the id {store_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method="POST",
    operation_description="Create an order",
    request_body=OrderSerializer,
    responses={201: OrderSerializer()},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order_endpoint(request):
    # TODO may want to change this to allow sellers to 
    # make orders for their customers as well
    if request.user.groups.filter(name="Customers").exists():
        data = request.data
        data["user"] = request.user.id
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        {"message": "You are not authorized to create orders"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@swagger_auto_schema(
    method="PUT",
    operation_description="Update an order",
    request_body=OrderSerializer,
    responses={200: OrderSerializer()},
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_order_endpoint(request):
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
        or request.user.groups.filter(name="Customers").exists()
    ):
        data = request.data
        try:
            order = Order.objects.get(id=data["id"])
            if (
                request.user.groups.filter(name="Admins").exists()
                or (
                    request.user.groups.filter(name="Sellers").exists()
                    and request.user.store == order.store
                )
                or order.user == request.user
            ):
                serializer = OrderSerializer(order, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                {"message": "You are not authorized to update this order"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Order.DoesNotExist:
            return Response(
                {"message": f"Order not found with the id {data['id']}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    return Response(
        {"message": "You are not authorized to update orders"},
        status=status.HTTP_401_UNAUTHORIZED,
    )
