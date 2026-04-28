from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path('', views.assessment_list, name='assessment_list'),
    path('create/', views.create_assessment, name='create_assessment'),
    path('me/', views.my_submissions, name='my_submissions'),
    path('submissions/', views.submission_list, name='submission_list'),
    path('<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('<int:assessment_id>/submit/', views.submit_assessment, name='submit_assessment'),
    path('submission/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('evaluate/', views.evaluate_view, name='evaluate'),
    path('evaluate/batch/', views.batch_evaluate_view, name='batch_evaluate'),
]