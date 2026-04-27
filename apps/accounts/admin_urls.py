from django.urls import path
from apps.accounts import admin_views as v

app_name = 'admin_panel'

urlpatterns = [
    path('users/',                  v.user_list,        name='user_list'),
    path('users/create/',           v.user_create,      name='user_create'),
    path('users/<int:pk>/',         v.user_detail,      name='user_detail'),
    path('users/<int:pk>/edit/',    v.user_edit,        name='user_edit'),
    path('users/<int:pk>/impersonate/', v.impersonate,  name='impersonate'),
    path('stop-impersonate/',       v.stop_impersonate, name='stop_impersonate'),
    path('audit/',                  v.audit_log,        name='audit_log'),
    path('audit/pdf/',              v.pdf_audit_log,    name='pdf_audit_log'),
    path('users/pdf/',              v.pdf_users,        name='pdf_users'),
]
