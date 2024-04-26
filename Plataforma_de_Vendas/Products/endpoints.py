#API endpoints for products
from django.http import JsonResponse
from django.contrib.auth import authenticate

from django.db.models import Q
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Product
from .serializers import ProductSerializer
from Stores.models import Store

import json

@swagger_auto_schema(
    method='get',
    responses={200: 'OK'},
    description='Get all products, all products from a specific store by store id,  or a specific product by product id'
)
@api_view(['GET'])
def get_products_endpoint(request, store_id=None, product_id=None):
    if store_id is not None:
        try:
            store = Store.objects.get(id=store_id)
            products = Product.objects.filter(store=store)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({"message": f"Store not found with the id {store_id}"}, status=status.HTTP_404_NOT_FOUND)
    elif product_id is not None:
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"message": f"Product not found with the id {product_id}"}, status=status.HTTP_404_NOT_FOUND)
    else:
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='q',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='Search query'
        )
    ],
    responses={200: 'OK'},
    description='Search for products by name or description'
)
@api_view(['GET'])
def search_for_product_endpoint(request, store_id=None):
    search_terms = request.GET.get('q', '').split(" ")
    query = Q()
    for term in search_terms:
        query |= Q(name__icontains=term) | Q(description__icontains=term)

    if store_id is not None:
        try:
            store = Store.objects.get(id=store_id)
            products = Product.objects.filter(query,store=store)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Store.DoesNotExist:
            return Response({"message": f"Store not found with the id {store_id}"}, status=status.HTTP_404_NOT_FOUND)


    products = Product.objects.filter(query)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'description', 'price', 'store_id'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Product name'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Product description'),
            'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Product price'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product quantity'),
            'store_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Store id'),
            'details': openapi.Schema(type=openapi.TYPE_STRING, description='Product details', default='{}'),
            'minimum_quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Minimum quantity for product for notifications'),
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Product status'),
        }
    ),
    responses={200: 'Created'}
)
@api_view(['POST'])
def add_product_endpoint(request):
    data = request.data
    store = Store.objects.get(id=data.get('store_id'))
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.store == store:

            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "You do not have permission to add a product to this store"}, status=status.HTTP_403_FORBIDDEN)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product id'),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Product name'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='Product description'),
            'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Product price'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product quantity'),
            'store_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Store id'),
            'details': openapi.Schema(type=openapi.TYPE_STRING, description='Product details', default='{}'),
            'minimum_quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Minimum quantity for product for notifications'),
            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Product status'),
        }
    ),
    responses={200: 'Updated'}
)
@api_view(['PUT'])
def update_product_endpoint(request):
    data = request.data
    product_id = data.get('id')
    try:
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.store == product.store:
                serializer = ProductSerializer(product, data=data)
                if serializer.is_valid():
                    serializer.save()
                    if data.get("quantity") <= serializer.data.get("minimum_quantity"):
                        send_notification(product.store.id, product.id, True, product.quantity)

                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "You do not have permission to update this product"}, status=status.HTTP_403_FORBIDDEN)
    except Product.DoesNotExist:
        return Response({"message": f"Product not found with the id {product_id}"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'quantity'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product id'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product quantity'),
        }
    ),
    responses={200: 'Updated'}
)
@api_view(['PUT'])
def update_product_stock_endpoint(request):
    data = request.data
    product_id = data.get('id')
    try:
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.store == product.store:
                product.quantity = data.get('quantity')
                product.save()
                if data.get("quantity") <= product.minimum_quantity:
                    send_notification(product.store.id, product.id, True, product.quantity)

                return Response({"message": "Product stock updated successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "You do not have permission to update this product"}, status=status.HTTP_403_FORBIDDEN)
    except Product.DoesNotExist:
        return Response({"message": f"Product not found with the id {product_id}"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'quantity'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product id'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product quantity'),
        }
    ),
    responses={200: 'Updated'}
)
@api_view(['PUT'])
def remove_stock_endpoint(request):
    data = request.data
    product_id = data.get('id')
    try:
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.store == product.store:
                if product.quantity < data.get('quantity'):
                    return Response({"message": "You cannot remove more stock than is available"}, status=status.HTTP_400_BAD_REQUEST)
                product.quantity -= data.get('quantity')
                product.save()
                if product.quantity <= product.minimum_quantity:
                    send_notification(product.store.id, product.id, True, product.quantity)
                return Response({"message": "Product stock updated successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "You do not have permission to update this product"}, status=status.HTTP_403_FORBIDDEN)
    except Product.DoesNotExist:
        return Response({"message": f"Product not found with the id {product_id}"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'quantity'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product id'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product quantity'),
        }
    ),
    responses={200: 'Updated'}
)
@api_view(['PUT'])
def add_stock_endpoint(request):
    data = request.data
    product_id = data.get('id')
    try:
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.store == product.store:
                product.quantity += data.get('quantity')
                product.save()
                return Response({"message": "Product stock updated successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "You do not have permission to update this product"}, status=status.HTTP_403_FORBIDDEN)
    except Product.DoesNotExist:
        return Response({"message": f"Product not found with the id {product_id}"}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Product id'),
        }
    ),
    responses={200: 'Updated'}
)
@api_view(['PUT'])
def remove_product_endpoint(request):
    data = request.data
    product_id = data.get('id')
    try:
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.store == product.store:
                product.is_active = False
                product.save()
                return Response({"message": "Product deactivated successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "You do not have permission to delete this product"}, status=status.HTTP_403_FORBIDDEN)
    except Product.DoesNotExist:
        return Response({"message": f"Product not found with the id {product_id}"}, status=status.HTTP_404_NOT_FOUND)

def send_notification(store_id, product_id, out_of_stock, current_stock):
    #TODO Implement notification system
    pass
