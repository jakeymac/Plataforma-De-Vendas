from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect



# Create your views here.


def logout_view(request):
    logout(request) #TODO UPDATE THIS TO SEND A REQUEST TO THE API TO LOGOUT TO MAINTAIN UNIFORMITY ACROSS THIS PLATFORM AND FUTURE APPS
    return redirect('/')
    
def login_page(request):
    return render(request, 'Accounts/login.html')

def register_account_page(request):
    return render(request, 'Accounts/register_account.html')

def register_store_page(request):
    return render(request, 'Accounts/register_store.html')

def view_user_account(request):
    return render(request, 'Accounts/user_account.html')

def view_store_account(request):
    return render(request, 'Accounts/store_account.html')

def view_admin_account(request):
    return render(request, 'Accounts/admin_account.html')

