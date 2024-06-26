from django import forms
from .models import CustomUser
from Stores.models import Store

class AccountRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'address', 'address_two', 'city', 'state', 'zip_code', 'country', 'phone_number', 'profile_picture', 'date_of_birth', 'notes']
            
class SellerRegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'address', 'address_two', 'city', 'state', 'zip_code', 'country', 'phone_number', 'profile_picture', 'date_of_birth', 'notes']
        
    store = forms.ModelChoiceField(queryset=Store.objects.all())
    stock_notifications = forms.BooleanField()

class StoreRegistrationForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description', 'url']
            