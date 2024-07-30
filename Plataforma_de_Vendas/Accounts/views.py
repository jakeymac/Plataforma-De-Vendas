from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect

from django.contrib.auth.forms import AuthenticationForm
from .forms import AccountRegistrationForm, SellerRegistrationForm, StoreRegistrationForm



# Create your views here.


def logout_view(request):
    logout(request) #TODO UPDATE THIS TO SEND A REQUEST TO THE API TO LOGOUT TO MAINTAIN UNIFORMITY ACROSS THIS PLATFORM AND FUTURE APPS
    return redirect('/')
    
def login_page(request):
     #TODO UPDATE THIS TO SEND A REQUEST TO THE API TO LOGOUT TO MAINTAIN UNIFORMITY ACROSS THIS PLATFORM AND FUTURE APPS
    if request.method =='POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
        
    return render(request, 'Accounts/login.html', {'form': form})

def register_account_page(request):
    form = AccountRegistrationForm()
    if request.method == 'POST':
        form = AccountRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    return render(request, 'Accounts/register_account.html', context={'form': form})

def register_seller_page(request):
    return render(request, 'Accounts/register_seller.html')

def view_user_account(request):
    return render(request, 'Accounts/user_account.html')

def view_store_account(request):
    return render(request, 'Accounts/store_account.html')

def view_admin_account(request):
    return render(request, 'Accounts/admin_account.html')

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
