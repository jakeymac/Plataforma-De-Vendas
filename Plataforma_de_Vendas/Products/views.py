from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import (
    InitialProductImage,
    InitialProductState,
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
        # TODO add a forbidden page to let users know what's happening
        return redirect("home")


@login_required
def edit_product_view(request, product_id):
    if (
        request.user.groups.filter(name="Sellers").exists()
        or request.user.groups.filter(name="Admins").exists()
    ):
        try:
            product = Product.objects.get(id=product_id)
            if product.store != request.user.store and not request.user.groups.filter(name="Admins").exists():
                # TODO add a forbidden page to let users know what's happening
                return redirect("home")

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
            # TODO add a 404 page to let users know what's
            # happening - that the product was not found
            return redirect("home")
    else:
        # TODO add a forbidden page to let users know what's happening
        return redirect("home")


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
        # TODO add a 404 page to let users know what's
        # happening - that the product was not found
        return redirect("home")
