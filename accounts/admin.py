from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
# from django.contrib.auth import get_user_model
# from .models import CustomUser, HrProfile, DeanProfile, OfficerProfile
from .models import *


# User = get_user_model()
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    # password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    # password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    # password1 = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    # password2 = forms.CharField(label='Password confirmation', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    error_messages = {
        'password_mismatch': ('The two password fields didn’t match.'),
    }
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )



    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)
    # def clean_password(self):
    #     # Check that the two password entries match
    #     password1 = self.cleaned_data.get('password1')
    #     password2 = self.cleaned_data.get('password2')
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError("Two passwords didn't match")
    #     if len(password1) < 8:
    #         raise forms.ValidationError("Password must have atleast 8 characters!")
    #     return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'is_active', 'is_admin','is_shopkeeper')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CustomUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_admin','is_shopkeeper' )
    list_filter = ('is_admin','is_shopkeeper')
    fieldsets = (
        (None, {'fields': ('username','email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('User Type', {'fields': ('is_active','is_admin','is_shopkeeper')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    ordering = ('username', 'email', 'first_name', 'last_name', )
    filter_horizontal = ()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'username',
                'email',
                'is_admin',
                'is_shopkeeper',
                'is_active',
            }

        # Prevent non-superusers from editing
        if (
            not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields |= {
                'username',
                'email',
                'is_admin',
                'is_shopkeeper',
                'is_active',
            }


        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled=True

        return form


    # Custom Actions
    actions = [
        'activate_users',
    ]


    def activate_users(self, request, queryset):
        cnt = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f'Activated {cnt} users.')

    activate_users.short_description = 'Activate Users'


    # Overidding user permissions regardless of their permissions.
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False



# Register the new UserAdmin...
admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(HrProfile)
# admin.site.register(DeanProfile)
# admin.site.register(OfficerProfile)
# Unregister the Group model from admin.
# since we're not using Django's built-in permissions,
admin.site.unregister(Group)
