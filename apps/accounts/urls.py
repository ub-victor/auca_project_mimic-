from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/',           views.login_view,           name='login'),
    path('signup/',          views.signup_view,          name='signup'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('dashboard/',       views.dashboard_view,       name='dashboard'),
    path('logout/',          views.logout_view,          name='logout'),
    path('profile/',         views.profile_view,         name='profile'),

    # Password reset
    path('password-reset/',                              auth_views.PasswordResetView.as_view(template_name='accounts/forgot_password.html'),         name='password_reset'),
    path('password-reset/done/',                         auth_views.PasswordResetDoneView.as_view(template_name='accounts/forgot_password.html'),     name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',     auth_views.PasswordResetConfirmView.as_view(template_name='accounts/forgot_password.html'),  name='password_reset_confirm'),
    path('password-reset-complete/',                     auth_views.PasswordResetCompleteView.as_view(template_name='accounts/login.html'),           name='password_reset_complete'),
]
