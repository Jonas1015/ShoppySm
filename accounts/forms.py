from django import forms
from .admin import UserCreationForm
from django.db import transaction
# from .models import CustomUser
from .models import *
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

class UserLoginForm(forms.Form):
    query = forms.CharField(label = 'Username/Email')
    password = forms.CharField(label = 'Password', widget = forms.PasswordInput)

    def clean(self, *args, **kwargs):
        query = self.cleaned_data.get('query')
        password = self.cleaned_data.get('password')
        user_qs_final = User.objects.filter(
            Q(username__iexact=query) |
            Q(email__iexact=query)
        ).distinct()
        if not user_qs_final.exists() and user_qs_final.count != 1:
            raise forms.ValidationError("Invalid Credentials!")
        user_obj = user_qs_final.first()
        if not user_obj.check_password(password):
            raise forms.ValidationError("Wrong username or password!!")
        self.cleaned_data["user_obj"] = user_obj
        return super(UserLoginForm, self).clean(*args, **kwargs)


class userUpdatingForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'is_active', 'is_admin', 'is_shopkeeper']


class ShopKeeperProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = ShopKeeperProfile
        fields = ['phone_number', 'profile_pic' ]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name' ]


class AdminProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = AdminProfile
        fields = ['phone_number','profile_pic' ]
