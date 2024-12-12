from django.shortcuts import render, redirect
from .models import Product, ProductSubcategory


def add_product_view(request):
    if request.user.is_authenticated and request.user.account_type == 'admin':
        return render(request, 'products/add_new_product.html')
    else:
        # TODO add a forbidden page to let users know what's happening
        return redirect('home')
    
def edit_product_view(request, product_id):
    if request.user.is_authenticated and request.user.account_type == 'admin':
        product = Product.objects.get(id=product_id)
        properties = product.properties
        subcategories = ProductSubcategory.objects.all()
        return render(request, 'products/edit_product.html', {'product': product, 'subcategories': subcategories, 'properties': properties})
    else:
        # TODO add a forbidden page to let users know what's happening
        return redirect('home')