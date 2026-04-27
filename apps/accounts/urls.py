from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .admin_views import stop_impersonate

urlpatterns = [
    path('', lambda request: __import__('django.shortcuts', fromlist=['redirect']).redirect('login')),
    path('login/',           views.login_view,           name='login'),
    path('signup/',          views.signup_view,          name='signup'),
    path('logout/',          views.logout_view,          name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('dashboard/',       views.dashboard_view,       name='dashboard'),
    path('staff/',           views.staff_area,           name='staff_dashboard'),
    path('profile/',         views.profile_view,         name='profile'),
    path('stop-impersonate/', stop_impersonate,          name='stop_impersonate'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

    path('student-area/',    views.student_area,         name='student_area'),
    path('lecturer-area/',   views.lecturer_area,        name='lecturer_area'),
    path('staff-area/',      views.staff_area,           name='staff_area'),
]
