from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('users/dashboard', views.users, name='users'),
    path('admin/all-users', views.allUsers, name = 'all-users'),
    path('admin/add-user', views.addNewUser, name = 'add-user'),
    path('admin/update-user/<int:id>/', views.updateUser, name = 'update-user'),
    path('admin/delete-user/<int:id>/', views.deleteUser, name = 'delete-user'),
    path('profile/', views.ProfileView, name='profile'),
    path('profile/update/', views.ProfileUpdateView, name='profile-update'),
    path('change-password/', views.change_password, name = 'change-password'),
    path('login/', views.loginView, name = 'login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'istock/home.html'), name = 'logout'),

    #=============================== pasword Reset =============================
    path('pasword-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name = 'password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name = 'password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name = 'password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name = 'password_reset_complete'),
]
