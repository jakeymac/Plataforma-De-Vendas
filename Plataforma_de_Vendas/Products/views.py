from django.shortcuts import render, redirect
from .models import (
    Product,
    ProductSubcategory,
    InitialProductState,
    InitialProductImage,
)
from django.contrib.auth.decorators import login_required


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
            if product.store != request.user.store:
                # TODO add a forbidden page to let users know what's happening
                return redirect("home")

            initial_product_state = InitialProductState.objects.create(
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

            images = product.productimage_set.all().order_by("order")
            for image in images:
                InitialProductImage.objects.create(
                    product=initial_product_state,
                    image=image.image,
                    order=image.order,
                    s3_key=image.s3_key,
                    original_created_at=image.created_at,
                    updated_at=image.updated_at,
                )

            properties = product.properties
            prices = product.prices
            subcategories = ProductSubcategory.objects.all()

            return render(
                request,
                "products/edit_product.html",
                {
                    "product": product,
                    "initial_product_state": initial_product_state,
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
        print(prices)
        images = product.productimage_set.all().order_by("order")
        print(images)
        return render(
            request,
            "products/view_product.html",
            {"product": product, "images": images, "prices": prices},
        )
    except Product.DoesNotExist:
        # TODO add a 404 page to let users know what's 
        # happening - that the product was not found
        return redirect("home")
