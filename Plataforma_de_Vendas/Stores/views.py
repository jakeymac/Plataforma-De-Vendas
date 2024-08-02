from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'Stores/home.html')

def view_my_store(request):
    if request.user.is_authenticated:
        if request.user.account_type == "seller":
            store = request.user.store
            return render(request, 'Stores/view_store.html', {"store": store})

def register_store_page(request):
    return render(request, 'Stores/register_store.html')