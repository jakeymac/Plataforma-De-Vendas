from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from Products.models import ProductCategory, ProductSubcategory, ProductTopSubcategory
from Stores.models import Store


# Create your views here.
def home(request):
    categories = ProductCategory.objects.all()
    categories_dict = {}
    for category in categories:
        categories_dict[category.category_name] = ProductSubcategory.objects.filter(
            category=category
        )

    top_subcategories = ProductTopSubcategory.objects.all()
    top_subcategories_dict = {}
    for top_subcategory in top_subcategories:
        top_subcategories_dict[top_subcategory] = ProductSubcategory.objects.filter(
            id=top_subcategory.subcategory_id
        )

    context = {
        "categories": categories_dict,
        "top_subcategories": top_subcategories_dict,
    }
    return render(request, "Stores/home.html", context)


def register_store_page(request):
    return render(request, "Stores/register_store.html")


@login_required
def view_my_store(request):
    if request.user.groups.filter(name="Sellers").exists():
        if request.user.store:
            store = request.user.store
            return redirect("view_store", store_url=store.store_url)
        else:
            raise Http404("There was an error finding your store.")
    else:
        raise PermissionDenied("You'll need to register as a seller first.")


def view_store(request, store_url):
    try:
        store = Store.objects.get(store_url=store_url)
        return render(request, "Stores/view_store.html", {"store": store})
    except Store.DoesNotExist:
        raise Http404("The store you are looking for does not exist.")

def product_search_page(request):
    return render(request, "Stores/product_search.html")


# TODO implement this view
# @login_required
# def store_admin_portal(request):
#     pass
