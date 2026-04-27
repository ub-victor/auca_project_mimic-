from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('create/',         views.course_create, name='create'),
    path('<int:pk>/edit/',  views.course_edit,   name='edit'),
    path('<int:pk>/delete/',views.course_delete, name='delete'),
    path('<int:pk>/enroll/',views.course_enroll, name='enroll'),
    path('<int:pk>/drop/',  views.course_drop,   name='drop'),
]
