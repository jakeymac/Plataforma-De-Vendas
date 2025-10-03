from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from .models import (
    Product,
    ProductSubcategory,
)


@login_required
def add_product_view(request):
    if (
        request.user.groups.filter(name="Sellers").exists()
        or request.user.groups.filter(name="Admins").exists()
    ):
        return render(request, "products/add_new_product.html")
    else:
        raise PermissionDenied("You do not have permission to add products")


@login_required
def edit_product_view(request, product_id):
    if (
        request.user.groups.filter(name="Sellers").exists()
        or request.user.groups.filter(name="Admins").exists()
    ):
        try:
            product = Product.objects.get(id=product_id)
            if (
                product.store != request.user.store
                and not request.user.groups.filter(name="Admins").exists()
            ):
                raise PermissionDenied("You do not have permission to edit this product")

            images = product.productimage_set.all().order_by("order")
            properties = product.properties
            prices = product.prices
            subcategories = ProductSubcategory.objects.all()

            return render(
                request,
                "products/edit_product.html",
                {
                    "product": product,
                    "images": images,
                    "subcategories": subcategories,
                    "properties": properties,
                    "prices": prices,
                },
            )
        except Product.DoesNotExist:
            return render(request, "products/product_not_found.html")
    else:
        raise PermissionDenied("You do not have permission to edit products")


def view_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        prices = product.prices
        images = product.productimage_set.all().order_by("order")
        return render(
            request,
            "products/view_product.html",
            {"product": product, "images": images, "prices": prices},
        )

    except Product.DoesNotExist:
        return render(request, "products/product_not_found.html")
