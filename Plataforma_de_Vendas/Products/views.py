from django.shortcuts import render, redirect
from .models import Product

# Create your views here.

def add_product_view(request):
    if request.user.is_authenticated and request.user.account_type == 'admin':
        return render(request, 'products/add_new_product.html')
    else:
        # TODO add a forbidden page to let users know what's happening
        return redirect('home')

    