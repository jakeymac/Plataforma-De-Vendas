from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render
from Products.models import ProductCategory, ProductSubcategory, ProductTopSubcategory
from Stores.models import Store
from Orders.models import Order


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
    if request.user.is_authenticated and request.user.groups.filter(name="Sellers").exists():
        if request.user.store and request.user.store.store_url == store_url:
            orders = Order.objects.filter(store=request.user.store).order_by("-created_at")[:10]
            return render(request, "Stores/store_dashboard.html", {"store": request.user.store, "recent_orders": orders})
    try:
        store = Store.objects.get(store_url=store_url)
        return render(request, "Stores/view_store.html", {"store": store})
    except Store.DoesNotExist:
        raise Http404("The store you are looking for does not exist.")
    
@login_required
def order_dashboard(request):
    if request.user.is_authenticated and request.user.groups.filter(name="Sellers").exists():
        if request.user.store:
            return render(request, "Stores/store_orders_dashboard.html", {"store": request.user.store})
        else:
            raise Http404("You do not have a store associated with your account.")
    else:
        raise PermissionDenied("You'll need to register as a seller first.")


def product_search_page(request):
    categories = ProductCategory.objects.all()
    subcategories = ProductSubcategory.objects.all()
    stores = Store.objects.all()
    context = {
        "categories": categories,
        "subcategories": subcategories,
        "stores": stores,
    }
    return render(request, "Stores/product_search.html", context)


# TODO implement this view
# @login_required
# def store_admin_portal(request):
#     pass
