# API endpoints for products
import json

from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from Orders.models import Order
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from Stores.models import Store

from .models import (
    InitialProductImage,
    InitialProductState,
    Product,
    ProductCategory,
    ProductImage,
    ProductInOrder,
    ProductSubcategory,
    ProductTopSubcategory,
)
from .serializers import (
    ProductCategorySerializer,
    ProductInOrderSerializer,
    ProductSerializer,
    ProductSubcategorySerializer,
    ProductTopSubcategorySerializer,
)


@swagger_auto_schema(
    method="get",
    responses={200: "OK"},
    description="Get all products by store id",
)
@api_view(["GET"])
def get_products_by_store_endpoint(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        products = Product.objects.filter(store=store)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Store.DoesNotExist:
        return Response(
            {"message": f"Store not found with the id {store_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(
        {"message": "There was an error retreiving the products"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# TODO this endpoint may not be secure, being able to just pull all the product endpoints
# + being able to confirm the existence or non-existence of a product by id


@swagger_auto_schema(
    method="get",
    responses={200: "OK"},
    description=("Get all products, or a specific product by product id"),
)
@api_view(["GET"])
def get_products_endpoint(request, product_id=None):
    if product_id is not None:
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"message": f"Product not found with the id {product_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

    else:
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response({"products": serializer.data}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="delete",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["id"],
        properties={
            "product_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Product id"),
        },
    ),
    responses={200: "Deleted"},
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_product_endpoint(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        # TODO add a check to see if the user is a seller and if they have permissions
        # to delete products and if they belong to the store that owns this product
        if (
            request.user.groups.filter(name="Admins").exists()
            or request.user.store == product.store
        ):
            initial_products = InitialProductState.objects.filter(product=product)
            with transaction.atomic():
                for initial_product in initial_products:
                    initial_product.delete()
                product.delete()
                return Response(
                    {"message": "Product removed successfully"},
                    status=status.HTTP_204_NO_CONTENT,
                )

        return Response(
            {"message": "You do not have permission to delete this product"},
            status=status.HTTP_403_FORBIDDEN,
        )

    except Product.DoesNotExist:
        return Response(
            {"message": f"Product not found with the id {product_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(
    method="get",
    responses={200: "OK"},
    description="Get all images for a product by product id",
)
@api_view(["GET"])
def product_images_endpoint(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        images = ProductImage.objects.filter(product=product)
        images = product.productimage_set.all().order_by("order")
        images_data = [{"id": image.id, "url": image.image.url} for image in images]
        return JsonResponse(
            {"product_id": product_id, "images": images_data}, status=status.HTTP_200_OK
        )
    except Product.DoesNotExist:
        return Response(
            {"message": f"Product not found with the id {product_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["product_id", "image"],
        properties={
            "product_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Product id"),
            "image": openapi.Schema(type=openapi.TYPE_FILE, description="Image file"),
        },
    ),
    responses={201: "Created"},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_image_endpoint(request):
    # TODO add a check to see if the user is a seller and if they have
    # permissions to add images and if the product belongs to the store
    # the seller belongs to
    data = request.data
    product_id = data.get("product_id")
    try:
        product = Product.objects.get(id=product_id)

        if request.user.groups.filter(name="Admins").exists() or (
            request.user.groups.filter(name="Sellers").exists()
            and request.user.store == product.store
        ):
            # TODO Add functionality to redo the order of the images
            # if adding just one image with the order specified
            if data.get("order") is not None:
                try:
                    order = int(data.get("order"))
                except Exception:
                    return Response(
                        {"message": "Invalid order, must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                last_image = (
                    ProductImage.objects.filter(product_id=product_id).order_by("-order").first()
                )
                if last_image:
                    order = last_image.order + 1
                else:
                    order = 0

            image_file = request.FILES.get("image")
            if not image_file:
                return Response(
                    {"message": "No image file provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # TODO add a checker to see if this image already exists (or with this name)
            image = ProductImage(product=product, image=image_file, order=order)
            image.save()
            return Response(
                {
                    "message": "Image added successfully",
                    "id": image.id,
                    "url": image.image.url,
                },
                status=status.HTTP_201_CREATED,
            )

        else:
            return Response(
                {"message": ("You do not have permission to add an image to this product")},
                status=status.HTTP_403_FORBIDDEN,
            )

    except Product.DoesNotExist:
        return Response(
            {"message": f"Product not found with the id {product_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(
    method="delete",
    responses={200: "OK"},
    description="Remove an image for a product by image id",
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_product_image_endpoint(request, image_id):
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
    ):
        try:
            image = ProductImage.objects.get(id=image_id)
            image.delete()
            return Response(
                {"message": "Image removed successfully"}, status=status.HTTP_204_NO_CONTENT
            )
        except ProductImage.DoesNotExist:
            return Response(
                {"message": f"Image not found with the id {image_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"message": "You do not have permission to remove this image"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="get",
    responses={200: "OK"},
    description="Get all products in an order by order id",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def products_in_order_endpoint(request, order_id):
    # TODO make this endpoint more secure since this
    # endpoint confirms the existence of an order or not
    try:
        order = Order.objects.get(id=order_id)
        if (
            request.user.groups.filter(name="Admins").exists()
            or (
                request.user.groups.filter(name="Sellers").exists()
                and request.user.store == order.store
            )
            or order.user == request.user
        ):
            products = ProductInOrder.objects.filter(order=order)
            serializer = ProductInOrderSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response(
            {"message": f"Order not found with the id {order_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(
    method="get",
    responses={200: "OK"},
    description="Get all products in a category by category id",
)
@api_view(["GET"])
def find_products_in_category_endpoint(request, category_id):
    try:
        category = ProductCategory.objects.get(id=category_id)
        subcategories = ProductSubcategory.objects.filter(category=category)
        products = Product.objects.filter(subcategory__in=subcategories)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ProductCategory.DoesNotExist:
        return Response(
            {"message": f"Category not found with the id {category_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(method="get", responses={200: "OK"}, description="Get all subcategories")
@api_view(["GET"])
def get_subcategories_endpoint(request):
    subcategories = ProductSubcategory.objects.all()
    if not subcategories:
        return Response({"message": "No subcategories found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductSubcategorySerializer(subcategories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get", responses={200: "OK"}, description="Get a category by category id"
)
@api_view(["GET"])
def get_subcategory_endpoint(request, subcategory_id):
    try:
        subcategory = ProductSubcategory.objects.get(id=subcategory_id)
        serializer = ProductSubcategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ProductSubcategory.DoesNotExist:
        return Response(
            {"message": f"Subcategory not found with the id {subcategory_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(
    method="get", responses={200: "OK"}, description="Get subcategories by category id"
)
@api_view(["GET"])
def get_subcategories_by_category_endpoint(request, category_id):
    try:
        category = ProductCategory.objects.get(id=category_id)
        subcategories = ProductSubcategory.objects.filter(category=category)
        serializer = ProductSubcategorySerializer(subcategories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ProductCategory.DoesNotExist:
        return Response(
            {"message": f"Category not found with the id {category_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(method="get", responses={200: "OK"}, description="Get all categories")
@api_view(["GET"])
def get_categories_endpoint(request):
    categories = ProductCategory.objects.all()
    if not categories:
        return Response({"message": "No categories found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductCategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get", responses={200: "OK"}, description="Get a category by category id"
)
@api_view(["GET"])
def get_category_endpoint(request, category_id):
    try:
        category = ProductCategory.objects.get(id=category_id)
        serializer = ProductCategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ProductCategory.DoesNotExist:
        return Response(
            {"message": f"Category not found with the id {category_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name", "category_id"],
        properties={
            "subcategory_name": openapi.Schema(
                type=openapi.TYPE_STRING, description="Subcategory name"
            ),
            "category_id": openapi.Schema(type=openapi.TYPE_STRING, description="Category id"),
            "subcategory_description": openapi.Schema(
                type=openapi.TYPE_STRING, description="Subcategory description"
            ),
        },
    ),
    responses={201: "Created"},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_subcategory_endpoint(request):
    # Use copy to allow for modification of the request data
    if request.user.groups.filter(name="Admins").exists():
        data = request.data
        category_id = data.get("category_id")
        try:
            # Check if the category exists
            ProductCategory.objects.get(id=category_id)
            serializer = ProductSubcategorySerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data.copy()
                response_data["message"] = "Subcategory added successfully"
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProductCategory.DoesNotExist:
            return Response(
                {"message": f"Category not found with the id {category_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"message": "You do not have permission to add a subcategory"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["name"],
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Category name"),
            "category_description": openapi.Schema(
                type=openapi.TYPE_STRING, description="Category description"
            ),
        },
    ),
    responses={201: "Created"},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_category_endpoint(request):
    if request.user.groups.filter(name="Admins"):
        data = request.data
        serializer = ProductCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_data = serializer.data.copy()
            response_data["message"] = "Category added successfully"
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {"message": "You do not have permission to add a category"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["category", "name"],
        properties={
            "category": openapi.Schema(type=openapi.TYPE_INTEGER, description="Category id"),
            "name": openapi.Schema(type=openapi.TYPE_STRING, description="Category name"),
            "category_description": openapi.Schema(
                type=openapi.TYPE_STRING, description="Category description"
            ),
        },
    ),
    responses={200: "Updated"},
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_category_endpoint(request):
    if request.user.groups.filter(name="Admins").exists():
        data = request.data
        category_id = data.get("category_id")
        try:
            category = ProductCategory.objects.get(id=category_id)
            serializer = ProductCategorySerializer(category, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data.copy()
                response_data["message"] = "Category updated successfully"
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProductCategory.DoesNotExist:
            return Response(
                {"message": f"Category not found with the id {category_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"message": "You do not have permission to update this category"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=[
            "subcategory",
            "subcategory_name",
            "subcategory_description" "category",
        ],
        properties={
            "subcategory": openapi.Schema(type=openapi.TYPE_INTEGER, description="Subcategory id"),
            "subcategory_name": openapi.Schema(
                type=openapi.TYPE_STRING, description="Subcategory name"
            ),
            "subcategory_description": openapi.Schema(
                type=openapi.TYPE_STRING, description="Subcategory description"
            ),
            "category": openapi.Schema(type=openapi.TYPE_INTEGER, description="Category id"),
        },
    ),
    responses={200: "Updated"},
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_subcategory_endpoint(request):
    if request.user.groups.filter(name="Admins").exists():
        # Use copy to allow for modification of the request data
        data = request.data
        subcategory_id = data.get("subcategory_id")
        try:
            subcategory = ProductSubcategory.objects.get(id=subcategory_id)
            serializer = ProductSubcategorySerializer(subcategory, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data.copy()
                response_data["message"] = "Subcategory updated successfully"
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProductSubcategory.DoesNotExist:
            return Response(
                {"message": f"Subcategory not found with the id {subcategory_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"message": "You do not have permission to update this subcategory"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="delete",
    responses={200: "OK"},
    description="Remove a category by category id",
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_category_endpoint(request, category_id):
    if request.user.groups.filter(name="Admins").exists():
        try:
            subcategories = ProductSubcategory.objects.filter(category=category_id)
            for subcategory in subcategories:
                subcategory.delete()
            category = ProductCategory.objects.get(id=category_id)
            category.delete()
            return Response(
                {"message": "Category removed successfully"}, status=status.HTTP_204_NO_CONTENT
            )
        except ProductCategory.DoesNotExist:
            return Response(
                {"category": f"Category not found with the id {category_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"message": "You do not have permission to remove this category"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="delete",
    responses={200: "OK"},
    description="Remove a subcategory by subcategory id",
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_subcategory_endpoint(request, subcategory_id):
    if request.user.groups.filter(name="Admins").exists():
        try:
            subcategory = ProductSubcategory.objects.get(id=subcategory_id)
            subcategory.delete()
            return Response(
                {"message": "Subcategory removed successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ProductSubcategory.DoesNotExist:
            return Response(
                {"message": f"Subcategory not found with the id {subcategory_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"message": "You do not have permission to remove this subcategory"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="GET",
    responses={200: "OK"},
    description=("Get all top subcategories"),
)
@api_view(["GET"])
def get_top_subcategories_endpoint(request):
    top_subcategories = ProductTopSubcategory.objects.all().order_by("order")
    response_data = {}
    for top_subcategory in top_subcategories:
        response_data[top_subcategory.order] = {
            "subcategory_name": top_subcategory.subcategory.subcategory_name,
            "subcategory_description": top_subcategory.subcategory.subcategory_description,
            "id": top_subcategory.subcategory.id,
        }
    return Response(response_data, status=status.HTTP_200_OK)


@swagger_auto_schema(method="PUT", responses={200: "OK"}, description="Update top subcategories")
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_top_subcategories_endpoint(request):
    if request.user.groups.filter(name="Admins").exists():
        data = request.data
        seen = set()
        duplicates = []
        # TODO could make this number a built-in setting to keep uniform across the project
        if len(request.data) != 6:
            return Response(
                {"message": "There must be 6 top subcategories"}, status=status.HTTP_400_BAD_REQUEST
            )
        for subcategory in request.data:
            if data.get(subcategory) in seen:
                duplicates.append(data.get(subcategory))
            else:
                seen.add(data.get(subcategory))
        if duplicates:
            return Response(
                {"message": "Duplicate subcategories found", "duplicates": duplicates},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organized_data = []

        # Order starts at 1
        not_found_subcategories = []
        for current_order, subcategory in enumerate(request.data, start=1):
            if not ProductSubcategory.objects.filter(id=data.get(subcategory)).exists():
                not_found_subcategories.append(data.get(subcategory))

            organized_data.append(
                {
                    "subcategory": data.get(subcategory),
                    "order": current_order,
                }
            )
        if not_found_subcategories:
            return Response(
                {
                    "message": f"Subcategories not found with id(s): {not_found_subcategories}",
                    "ids": not_found_subcategories,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProductTopSubcategorySerializer(data=organized_data, many=True)
        # Delete the top subcategories that are being updated
        # TODO perhaps add a rollback to make sure these changes do get done fully and properly
        for subcategory in organized_data:
            ProductTopSubcategory.objects.filter(order=subcategory.get("order")).delete()
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = {
            "message": "Top subcategories updated successfully",
            "data": serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "You do not have permission to update top subcategories"},
            status=status.HTTP_403_FORBIDDEN,
        )


@swagger_auto_schema(
    method="post",
    responses={200: openapi.Response("Success", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    description="Add a new product",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_endpoint(request):
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
    ):
        data = request.data
        if Product.objects.filter(product_name=data.get("product_name")).exists():
            return Response(
                {"message": "Product with that name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            product_serializer = ProductSerializer(data=data, partial=True)
            product_serializer.is_valid(raise_exception=True)
            product_serializer.save()
            response_data = product_serializer.data.copy()
            response_data["message"] = "Product added successfully"
            return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(
        {"message": "You do not have permission to add a product"},
        status=status.HTTP_403_FORBIDDEN,
    )


@swagger_auto_schema(
    method="POST",
    responses={200: openapi.Response("Success", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    description="Rollback a product to a previous state",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rollback_product_changes_endpoint(request):
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
    ):
        data = request.data

        product_not_found = False
        initial_state_not_found = False
        try:
            product = Product.objects.get(id=data.get("product_id"))
            if (
                not request.user.groups.filter(name="Admins").exists()
                and request.user.store != product.store
            ):
                return Response(
                    {"message": "You do not have permission to rollback this product"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Product.DoesNotExist:
            product_not_found = True

        try:
            initial_state = InitialProductState.objects.get(id=data.get("initial_product_state_id"))
        except InitialProductState.DoesNotExist:
            initial_state_not_found = True

        if product_not_found and initial_state_not_found:
            return Response(
                {
                    "message": (
                        f"Product with id {data.get('product_id')} and initial product "
                        f"state with id {data.get('initial_product_state_id')} not found"
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        elif product_not_found:
            return Response(
                {"message": f"Product not found with the id {data.get('product_id')}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        elif initial_state_not_found:
            return Response(
                {
                    "message": (
                        "Initial product state not found with the id "
                        f"{data.get('initial_product_state_id')}"
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        else:
            with transaction.atomic():
                product.store = initial_state.store
                product.subcategory = initial_state.subcategory
                product.product_name = initial_state.product_name
                product.product_description = initial_state.product_description
                product.properties = initial_state.properties
                product.is_active = initial_state.is_active
                product.draft = initial_state.draft
                product.prices = initial_state.prices
                product.save()

                for image in product.productimage_set.all():
                    image.delete()

                for initial_image in initial_state.initialproductimage_set.all():
                    ProductImage.objects.create(
                        product=product,
                        image=initial_image.image,
                        order=initial_image.order,
                    )

                    initial_image.delete()

                initial_state.delete()

                return Response(
                    {"message": "Product rolled back successfully"},
                    status=status.HTTP_200_OK,
                )

    return Response(
        {"message": "You do not have permission to rollback products"},
        status=status.HTTP_403_FORBIDDEN,
    )


@swagger_auto_schema(
    method="POST",
    responses={200: openapi.Response("Success", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    description="Create an initial state for a product to rollback to",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_initial_product_state_endpoint(request):
    # TODO Could update all of this to not create a new initial state every
    # time each time the edit product page is reloaded for example
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
    ):
        data = request.data
        product_id = data.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
            if (
                not request.user.groups.filter(name="Admins").exists()
                and request.user.store != product.store
            ):
                return Response(
                    {
                        "message": (
                            "You do not have permission to create an initial product state "
                            "for this product"
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            initial_state = InitialProductState(
                product=product,
                store=product.store,
                subcategory=product.subcategory,
                product_name=product.product_name,
                product_description=product.product_description,
                properties=product.properties,
                is_active=product.is_active,
                draft=product.draft,
                prices=product.prices,
                original_created_at=product.created_at,
            )
            initial_state.save()

            for image in product.productimage_set.all():
                InitialProductImage.objects.create(
                    initial_product=initial_state,
                    image=image.image,
                    order=image.order,
                    s3_key=image.s3_key,
                    original_created_at=image.created_at,
                    updated_at=image.updated_at,
                )

            return Response(
                {
                    "message": "Initial product state created successfully",
                    "initial_product_state_id": initial_state.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Product.DoesNotExist:
            return Response(
                {"message": f"Product not found with the id {product_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

    return Response(
        {"message": "You do not have permission to create initial product states"},
        status=status.HTTP_403_FORBIDDEN,
    )


# This endpoint auto saves a product, without deleting the initial state of
# the product, and without deleting the images of the product in storage
@swagger_auto_schema(
    method="post",
    responses={200: openapi.Response("Success", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    description="Autosave a product",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def autosave_product_endpoint(request):
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
    ):
        data = request.data
        product_id = data.get("product_id")
        try:
            # Get the product and update it with the new data
            product = Product.objects.get(id=product_id)
            if (
                not request.user.groups.filter(name="Admins").exists()
                and request.user.store != product.store
            ):
                return Response(
                    {"message": "You do not have permission to autosave this product"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProductSerializer(product, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            order = 0
            ids_not_found = []
            for image_id in data.get("image_ids"):
                try:
                    product_image = ProductImage.objects.get(id=image_id)
                    product_image.order = order
                    product_image.save()
                    product_image.refresh_from_db()
                    order += 1
                except ProductImage.DoesNotExist:
                    ids_not_found.append(image_id)

            if ids_not_found:
                return Response(
                    {"message": f"Images not found with the ids {ids_not_found}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {"message": "Product autosaved successfully"}, status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {"message": f"Product not found with the id {product_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

    return Response(
        {"message": "You do not have permission to autosave products"},
        status=status.HTTP_403_FORBIDDEN,
    )


@swagger_auto_schema(
    method="post",
    responses={200: openapi.Response("Success", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    description="Final save a product",
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def final_save_product_endpoint(request):
    """
    This endpoint finalizes the save of a product, deleting the initial state
    of the product, and deleting the images of the product in storage
    """
    if (
        request.user.groups.filter(name="Admins").exists()
        or request.user.groups.filter(name="Sellers").exists()
    ):
        data = request.data
        product_id = data.get("product_id")
        try:
            # Get the product and update it with the new data
            product = Product.objects.get(id=product_id)
            if (
                not request.user.groups.filter(name="Admins").exists()
                and request.user.store != product.store
            ):
                return Response(
                    {"message": "You do not have permission to save this product"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProductSerializer(product, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            order = 0
            ids_not_found = []
            for image_id in data.get("image_ids"):
                try:
                    product_image = ProductImage.objects.get(id=image_id)
                    product_image.order = order
                    product_image.save()
                    order += 1
                except ProductImage.DoesNotExist:
                    ids_not_found.append(image_id)
            if ids_not_found:
                return Response(
                    {"message": f"Images not found with the ids {ids_not_found}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            initial_states = InitialProductState.objects.filter(product=product)
            for initial_state in initial_states:
                for image in initial_state.initialproductimage_set.all():
                    image.delete()
                initial_state.delete()

            return Response({"message": "Product saved successfully"}, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response(
                {"message": f"Product not found with the id {product_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

    return Response(
        {"message": "You do not have permission to save products"},
        status=status.HTTP_403_FORBIDDEN,
    )


@swagger_auto_schema(
    method="get",
    responses={200: openapi.Response("Success", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    description="Product search results",
)
@api_view(["GET"])
def product_search_endpoint(request):
    """
    Endpoint used in the product search page.
    This endpoint supports filtering, sorting, and pagination
    """
    search = request.GET.get("search", "")
    sort = request.GET.get("sort", "newest")
    filters = request.GET.get("filters", "{}")
    try:
        filters = json.loads(filters)
    except json.JSONDecodeError:
        return Response(
            {"message": "Invalid filters format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    queryset = Product.objects.all()

    if search:
        queryset = queryset.filter(
            Q(product_name__icontains=search)
            | Q(product_description__icontains=search)
            | Q(subcategory__subcategory_name__icontains=search)
        )

    # TODO need to decide on a default sort order
    if sort:
        sort_map = {
            "price-asc": "prices__amount",
            "price-desc": "-prices__amount",
            "name-asc": "product_name",
            "name-desc": "-product_name",
            "newest": "-created_at",
            "oldest": "created_at",
        }
        if sort in sort_map:
            sort_parameter = sort_map[sort]
        else:
            return Response(
                {"message": f"Invalid sort parameter: {sort}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.order_by(sort_parameter)

    invalid_filters = []
    if filters:
        filter_map = {
            "categories": "subcategory__category__id",
            "subcategories": "subcategory__id",
            "stores": "store__id",
            "category": "subcategory__category__id",
            "subcategory": "subcategory__id",
            "store": "store__id",
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
                {"message": f"Invalid filter parameter(s): {', '.join(invalid_filters)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    paginator = PageNumberPagination()
    # TODO we could make this part of the query - leave this as default for now
    paginator.page_size = 12
    paginated_qs = paginator.paginate_queryset(queryset, request)

    total_product_count = queryset.count()
    total_page_count = paginator.page.paginator.num_pages

    serializer = ProductSerializer(paginated_qs, many=True)
    products_data = serializer.data
    for product_dict, product_instance in zip(products_data, paginated_qs):
        product_dict["product_images"] = [
            {
                "id": image.id,
                "image": image.image.url,
                "order": image.order,
                "s3_key": image.s3_key,
            }
            for image in product_instance.productimage_set.all()
        ]

    return Response(
        {
            "product_count": total_product_count,
            "page_count": total_page_count,
            "next_page": paginator.get_next_link(),
            "previous_page": paginator.get_previous_link(),
            "products": products_data,
        },
        status=status.HTTP_200_OK,
    )
