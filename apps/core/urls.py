from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('analytics/',           views.analytics_dashboard, name='analytics'),
    path('timetable/download/',  views.timetable_download,  name='timetable_download'),
]
