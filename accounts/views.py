from django.shortcuts import redirect, reverse, render, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import get_template, render_to_string
from django.views.generic import TemplateView, View, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login, get_user_model, logout
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
# from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from .models import CustomUser
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from .models import *
from .forms import *
from .admin import *
from .decorators import *



@login_required
def users(request):
    myTemplate = 'accounts/dashboard.html'
    context = {}
    return render(request, myTemplate, context)


@login_required
@admin_login_required
def allUsers(request):
    users = CustomUser.objects.all()
    query = request.GET.get("q")
    if query:
        if users.filter(Q(first_name__icontains = query)| Q(last_name__icontains = query)):
            users = users.filter(Q(first_name__icontains = query)| Q(last_name__icontains = query))

        elif users.filter(Q(username__icontains = query)):
            users = users.filter(Q(username__icontains = query))

        else:
            users = CustomUser.objects.all()
            messages.warning(request, f'No results found!')
    context = {
        'users': users
    }
    myTemplate = 'accounts/allUsers.html'
    return render(request, myTemplate, context)

@login_required
@admin_login_required
def addNewUser(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, f'New User created successfully!!')
            return redirect('all-users')
    myTemplate = 'accounts/addUser.html'
    context = {
        'form' : form,
    }
    return render(request, myTemplate, context)


@login_required
@admin_login_required
def updateUser(request, id):
    instance = get_object_or_404(CustomUser, id = id)
    form = userUpdatingForm(request.POST or None, instance = instance)
    if form.is_valid():
        form.save()
        messages.success(request, f'User has been updated successifully!')
        return redirect ('all-users')
    context = {
        'form': form,
        # 'get_form':get_form,
    }
    myTemplate = 'accounts/updateUser.html'
    return render(request, myTemplate, context)


@login_required
@admin_login_required
def deleteUser(request, id):
    instance = get_object_or_404(CustomUser, id = id)
    instance.delete()
    messages.success(request, 'User deleted successifully!!')
    return redirect('all-users')

def loginView(request, *args, **kwargs):
    form = UserLoginForm()
    if request.method == 'POST':
        form = UserLoginForm(request.POST or None)
        if form.is_valid():
            user_obj = form.cleaned_data.get('user_obj')
            login(request, user_obj)
            return HttpResponseRedirect('/')
    myTemplate = 'accounts/login.html'
    context = {
        'form':form
    }
    return render(request, myTemplate, context)

@login_required
class UserLogoutView(LogoutView):
    template_name = 'accounts/logout.html'



@login_required
def ProfileView(request):

    if request.user.is_admin:
        profile = AdminProfile.objects.get(user = request.user)
    elif request.user.is_shopkeeper:
        profile = ShopKeeperProfile.objects.get(user = request.user)
    # elif request.user.is_officer:
    #     profile = OfficerProfile.objects.get(user = request.user)
    else:
        message = 'You have no permission to view this page'
        context = {
            'message': message
        }
        return render(request, 'accounts/profile.html', context)

        profile.user.save()

    context = {
        'profile': profile,
    }

    return render(request, 'accounts/profile.html', context)

@login_required
def ProfileUpdateView(request):
    user_form = UserUpdateForm(instance = request.user)
    if request.user.is_admin:
        profile_form = AdminProfileUpdateForm(instance = request.user.adminprofile)
        profile = AdminProfile.objects.get(user = request.user)

    elif request.user.is_shopkeeper:
        profile_form = ShopKeeperProfileUpdateForm(instance = request.user.shopkeeperprofile)
        profile = ShopKeeperProfile.objects.get(user = request.user)

    # elif request.user.is_officer:
    #     profile_form = OfficerProfileUpdateForm(instance = request.user.officerprofile)
    #     profile = OfficerProfile.objects.get(user = request.user)

    else :
        messages.warning(request, f'You have no permission to view this page')
        return redirect('dashboard')

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance = request.user)

        if request.user.is_admin:
            profile_form = AdminProfileUpdateForm(request.POST,
                                        request.FILES,
                                        instance = request.user.adminprofile)
            profile = AdminProfile.objects.get(user = request.user)

        elif request.user.is_shopkeeper:
            profile_form = ShopKeeperProfileUpdateForm(request.POST,
                                        request.FILES, instance = request.user.shopkeeperprofile)
            profile = ShopKeeperProfile.objects.get(user = request.user)
        # elif request.user.is_officer:
        #     profile_form = OfficerProfileUpdateForm(request.POST,
        #                                 request.FILES, instance = request.user.officerprofile)
        #     profile = OfficerProfile.objects.get(user = request.user)
        else:
            return redirect('accounts:profile')
            #Saving my newly updated forms
        if profile_form.is_valid() and user_form.is_valid():
            if request.user.is_admin:
                profiles = AdminProfile.objects.all()
            elif request.user.is_shopkeeper:
                profiles = ShopKeeperProfile.objects.all()
            # elif request.user.is_officer:
            #     profiles = OfficerProfile.objects.all()
            for profile in profiles:
                if profile.phone_number:
                    if profile_form.cleaned_data['phone_number'] == profile.phone_number:
                        messages.info(request, f'This number is already used by someone!')
                        return redirect('accounts:profile-update')
            profile_form.save()
            user_form.save()
            messages.success(request, f'You have successfully updated your profile! ')
            return redirect('accounts:profile')

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
        }
    return render(request, 'accounts/update.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, f'Password successfully changed!!')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    myTemplate = 'accounts/change_password.html'
    context = {
        'form': form,
    }
    return render(request, myTemplate, context)
