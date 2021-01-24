from django.core.exceptions import PermissionDenied
from accounts.models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test

# ======================== Check HR role =======================================
s_login_required = user_passes_test(lambda u: True if u.is_shopkeeper else False)

def shopkeeper_login_required(view_func):
    decorated_view_func = login_required(s_login_required(view_func))
    return decorated_view_func

# ============================= Check Dean Role ================================
a_login_required = user_passes_test(lambda u: True if u.is_admin else False)

def admin_login_required(view_func):
    decorated_view_func = login_required(a_login_required(view_func))
    return decorated_view_func

# ========================= Check Officer role =================================
# o_login_required = user_passes_test(lambda u: True if u.is_officer else False)
#
# def officer_login_required(view_func):
#     decorated_view_func = login_required(o_login_required(view_func))
#     return decorated_view_func

# ========================= Check Superuser role =================================
super_login_required = user_passes_test(lambda u: True if u.is_superuser else False)

def superuser_login_required(view_func):
    decorated_view_func = login_required(super_login_required(view_func))
    return decorated_view_func
