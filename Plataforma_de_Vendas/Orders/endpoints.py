#API endpoints for orders
from django.http import JsonResponse
from django.contrib.auth import authenticate

from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Order
from .serializers import OrderSerializer

import json

@swagger_auto_schema(method='GET',
    operation_description="Get all orders",
    responses={200: OrderSerializer(many=True)})
@api_view(['GET'])
def get_orders_endpoint(request):
    if request.user.is_authenticated and request.user.account_type == 'admin':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get an order by ID",
    responses={200: OrderSerializer()})
@api_view(['GET'])
def get_order_endpoint(request, order_id):
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(id=order_id)
            if request.user.account_type == 'admin' or (request.user.account_type == "seller" and order.store == request.user.store) or order.user == request.user:
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "You are not authorized to view this order"}, status=status.HTTP_401_UNAUTHORIZED)

        except Order.DoesNotExist:
            return Response({"message": f"Order not found with the id {order_id}"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"message": "You are not authorized to view this order"}, status=status.HTTP_401_UNAUTHORIZED)

    
@swagger_auto_schema(method='GET',
    operation_description="Get orders by user ID",
    responses={200: OrderSerializer(many=True)})
@api_view(['GET'])
def get_orders_by_user_endpoint(request, user_id):
    if request.user.is_authenticated and (request.user.account_type == 'admin' or request.user.id == user_id):
        try:
            user_object = CustomUser.objects.get(id=user_id)
            orders = Order.objects.filter(user=user_object)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"message": f"User not found with the id {user_id}"}, status=status.HTTP_404_NOT_FOUND)
        
    
    return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='GET',
    operation_description="Get orders by store ID",
    responses={200: OrderSerializer(many=True)})
@api_view(['GET'])
def get_orders_by_store_endpoint(request, store_id):
    if request.user.is_authenticated and request.user.account_type == 'admin':
        try:
            store = Store.objects.get(id=store_id)
            orders = Order.objects.filter(store=store)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({"message": f"Store not found with the id {store_id}"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='POST',
    operation_description="Create an order",
    request_body=OrderSerializer,
    responses={201: OrderSerializer()})
@api_view(['POST'])
def create_order_endpoint(request):
    if request.user.is_authenticated and request.user.account_type == "customer" or request.user.account_type == "seller":
        data = request.data
        data['user'] = request.user.id
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "You are not authorized to create orders"}, status=status.HTTP_401_UNAUTHORIZED)

@swagger_auto_schema(method='PUT',
    operation_description="Update an order",
    request_body=OrderSerializer,
    responses={200: OrderSerializer()})
@api_view(['PUT'])
def update_order_endpoint(request):
    if request.user.is_authenticated and request.user.account_type == "customer" or request.user.account_type == "seller":
        data = request.data
        try:
            order = Order.objects.get(id=data['id'])
            if request.user.account_type == 'admin' or (request.user.account_type == "seller" and order.store == request.user.store) or order.user == request.user:
                serializer = OrderSerializer(order, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "You are not authorized to update this order"}, status=status.HTTP_401_UNAUTHORIZED)
        except Order.DoesNotExist:
            return Response({"message": f"Order not found with the id {data['id']}"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"message": "You are not authorized to update orders"}, status=status.HTTP_401_UNAUTHORIZED)