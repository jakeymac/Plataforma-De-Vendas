# API endpoints for orders
import json

from Accounts.models import CustomUser
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from Stores.models import Store

from .models import Order
from .serializers import OrderSerializer


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
        # TODO add a check to see if the seller is allowed to view the order (MAYBE)
        if (
            request.user.groups.filter(name="Admins").exists()
            or (request.user.groups.filter(name="Sellers") and order.store == request.user.store)
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

    return Response(
        {"error": "You are not authorized to view these orders"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


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
        request.user.groups.filter(name="Sellers").exists() and request.user.store.id == store_id
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
    return Response(
        {"error": "You are not authorized to view these orders"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_orders_endpoint(request):

    search = request.GET.get("search", "")
    sort = request.GET.get("sort", "newest")
    filters = request.GET.get("filters", "{}")

    try:
        filters = json.loads(filters)
    except json.JSONDecodeError:
        return Response(
            {"message": "Invalid filters format."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    queryset = Order.objects.all()

    if search:
        queryset = queryset.filter(
            Q(user__username__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(store__store_name__icontains=search)
            | Q(tracking_code__icontains=search)
        )

    if sort:
        sort_map = {
            "newest": "-created_at",
            "oldest": "created_at",
            "highest_total": "-total",
            "lowest_total": "total",
        }
        if sort in sort_map:
            sort_parameter = sort_map[sort]
        else:
            valid_options = ", ".join(sort_map.keys())
            return Response(
                {"message": f"Invalid sort option '{sort}'. Valid options are: {valid_options}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.order_by(sort_parameter)

    invalid_filters = []
    if filters:
        filter_map = {
            "status": "status",
            "stores": "store__id",
            "users": "user__id",
        }
        for filter in filters:
            if filter in filter_map:
                filter_parameter = filter_map[filter]
                filter_value = filters[filter]
                if filter_value:
                    if isinstance(filter_value, list):
                        queryset = queryset.filter(**{f"{filter_parameter}__in": filter_value})
                    else:
                        queryset = queryset.filter(**{filter_parameter: filter_value})
            else:
                invalid_filters.append(filter)

        if invalid_filters:
            return Response(
                {"message": f"Invalid filter options: {', '.join(invalid_filters)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_qs = paginator.paginate_queryset(queryset, request)
    total_order_count = queryset.count()
    total_page_count = paginator.page.paginator.num_pages

    serializer = OrderSerializer(paginated_qs, many=True)
    orders_data = serializer.data

    return Response(
        {
            "orders": orders_data,
            "order_count": total_order_count,
            "page_count": total_page_count,
            "next_page": paginator.get_next_link(),
            "previous_page": paginator.get_previous_link(),
        },
        status=status.HTTP_200_OK,
    )
