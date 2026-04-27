from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path("", views.evaluator_page, name="evaluator"),
    path("evaluate/", views.evaluate_view, name="evaluate"),
    path("evaluate/batch/", views.batch_evaluate_view, name="batch_evaluate"),
]
