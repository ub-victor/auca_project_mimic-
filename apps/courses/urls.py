from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/unenroll/', views.unenroll_course, name='unenroll_course'),
    path('timetable/', views.timetable, name='timetable'),
    path('lecturer/', views.lecturer_courses, name='lecturer_courses'),
    path('users/', views.user_management, name='user_management'),
]