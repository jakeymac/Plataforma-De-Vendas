from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from Products.models import ProductCategory, ProductSubcategory, ProductTopSubcategory


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


@login_required
def view_my_store(request):
    if request.user.groups.filter(name="Sellers").exists():
        if request.user.store:
            store = request.user.store
            return render(request, "Stores/view_store.html", {"store": store})
        else:
            # TODO add a 404 page to let users know what's
            # happening - that their store was not found
            return redirect("home")
    else:
        # TODO add a 404 page to let users know that they
        # need to register
        return redirect("home")


def register_store_page(request):
    return render(request, "Stores/register_store.html")
