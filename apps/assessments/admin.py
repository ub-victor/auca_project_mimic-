from django.contrib import admin
from .models import Assessment, Question, Submission, SubmissionAnswer


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "assessment_type", "total_marks", "due_date", "created_by")
    list_filter = ("assessment_type", "course")
    search_fields = ("title", "course__code", "course__title", "created_by__username")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("assessment", "order", "max_score")
    list_filter = ("assessment",)
    search_fields = ("assessment__title", "prompt")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("assessment", "student", "status", "submitted_at", "ai_score")
    list_filter = ("status", "assessment")
    search_fields = ("assessment__title", "student__username", "student__email")


@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = ("submission", "question", "score")
    list_filter = ("question__assessment",)
    search_fields = ("submission__student__username", "question__prompt")
