from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect

from Products.models import (
    Product,
    ProductCategory,
    ProductSubcategory,
    ProductTopSubcategory,
)

import json


def is_admin(user):
    return user.is_authenticated and user.groups.filter(name="Admins").exists()


@login_required
@user_passes_test(is_admin, login_url="/login")
def admin_portal(request):
    categories = ProductCategory.objects.all()
    subcategories = ProductSubcategory.objects.all()
    categories_json = list(ProductCategory.objects.values())
    subcategories_json = list(ProductSubcategory.objects.values())
    top_subcategories_query = ProductTopSubcategory.objects.all()
    products = Product.objects.all().order_by("product_name")
    products_json = list(
        Product.objects.values("id", "product_name", "product_description")
    )

    context = {
        "categories": categories,
        "subcategories": subcategories,
        "products": products,
        "categories_json": json.dumps(categories_json),
        "subcategories_json": json.dumps(subcategories_json),
        "products_json": json.dumps(products_json),
    }

    for top_subcategory in top_subcategories_query:
        context[f"top_subcategory_{top_subcategory.order}"] = (
            top_subcategory.subcategory.id
        )

    return render(request, "Accounts/admin_portal.html", context=context)


def logout_view(request):
    logout(
        request
    )  
    # TODO UPDATE THIS TO SEND A REQUEST TO THE API TO LOGOUT TO 
    # MAINTAIN UNIFORMITY ACROSS THIS PLATFORM AND FUTURE APPS
    return redirect("/")


def login_page(request):
    next_link = request.GET.get("next", "/")
    context = {
        "next_link": next_link
    }  # TODO could make something like this into a DRY decorator to use in other pages
    return render(request, "Accounts/login.html", context=context)


def register_account_page(request):
    return render(request, "Accounts/register_account.html")


def register_seller_page(request):
    return render(request, "Accounts/register_seller.html")


@login_required
def view_account(request):
    if request.user.groups.filter(name="Customers").exists():
        return render(request, "Accounts/view_customer_account.html")
    elif request.user.groups.filter(name="Sellers").exists():
        return render(request, "Accounts/view_seller_account.html")
    elif request.user.groups.filter(name="Admins").exists():
        return render(request, "Accounts/view_admin_account.html")



