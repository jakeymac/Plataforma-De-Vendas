from django.shortcuts import render
from .models import Product

# Create your views here.

def add_new_product(request):
    new_product = Product()
    new_product.save()
    context = {"product_id": new_product.id}
    return render(request, 'Products/add_new_product.html', context)