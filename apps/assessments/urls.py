from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('',                                    views.assignment_list,    name='assignment_list'),
    path('create/',                             views.assignment_create,  name='assignment_create'),
    path('<int:pk>/',                           views.assignment_detail,  name='assignment_detail'),
    path('<int:assignment_pk>/grade/',          views.grade_submissions,  name='grade_submissions'),
    path('my-results/',                         views.my_results,         name='my_results'),
    path('evaluator/',                          views.evaluator_page,     name='evaluator'),
    path('evaluate/',                           views.evaluate_view,      name='evaluate'),
    path('evaluate/batch/',                     views.batch_evaluate_view,name='batch_evaluate'),
]
