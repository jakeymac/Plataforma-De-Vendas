from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm

from Products.models import ProductCategory, ProductSubcategory, ProductTopSubcategory

import json

def admin_portal(request):
    if request.user.is_authenticated:
        if request.user.account_type == "admin" and request.user.is_staff:
            categories = ProductCategory.objects.all()
            subcategories = ProductSubcategory.objects.all()
            categories_json = list(ProductCategory.objects.values())
            subcategories_json = list(ProductSubcategory.objects.values())            
            top_subcategories_query = ProductTopSubcategory.objects.all()

            context = {"categories": categories,
                       "subcategories": subcategories, 
                       "categories_json": json.dumps(categories_json), 
                       "subcategories_json": json.dumps(subcategories_json)}

            for top_subcategory in top_subcategories_query:
                context[f"top_subcategory_{top_subcategory.order}"] = top_subcategory.subcategory.id
            

            return render(request, 'Accounts/admin_portal.html', context=context)
    return redirect('/login')

def logout_view(request):
    logout(request) #TODO UPDATE THIS TO SEND A REQUEST TO THE API TO LOGOUT TO MAINTAIN UNIFORMITY ACROSS THIS PLATFORM AND FUTURE APPS
    return redirect('/')
    
def login_page(request):
    next_link = request.GET.get("next", "/")
    context = {"next_link": next_link}
    return render(request, 'Accounts/login.html', context=context)

def register_account_page(request):
    return render(request, 'Accounts/register_account.html')

def register_seller_page(request):
    return render(request, 'Accounts/register_seller.html')

def view_account(request):
    if request.user.is_authenticated:
        if request.user.account_type == "customer":
            return render(request, 'Accounts/view_customer_account.html')
        elif request.user.account_type == "seller": 
            return render(request, 'Accounts/view_seller_account.html')
        elif request.user.account_type == "admin":
            return render(request, 'Accounts/view_admin_account.html')
    
    else:
        next_url = request.get_full_path()
        return redirect(f'/login?next={next_url}')
        

def retrieve_profile_picture(request, username):
    if request.user.is_authenticated:
        if request.user.account_type == 'admin' or request.user.username == username:
            user = CustomUser.objects.get(username=username)
            if user.profile_picture:
                file_path = os.path.join(settings.MEDIA_ROOT, "profile_pictures", user.profile_picture)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        response = HttpResponse(file.read(), content_type="image")
                        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                        response['status'] = 200
                        return response
                return HttpResponse({"error": "Issue retreiving profile picture."}, status=404)
            return HttpResponse({"error": "No profile picture specified"}, status=400)
    return HttpResponse({"error": "Unauthorized"}, status=400)
