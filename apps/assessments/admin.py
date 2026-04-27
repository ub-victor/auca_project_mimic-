from django.contrib import admin
from .models import Assessment, Question, Answer


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'assessment_type', 'total_marks', 'due_date', 'created_by')
    search_fields = ('title', 'course__code', 'course__title')
    list_filter = ('assessment_type', 'course', 'due_date')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'question_text', 'marks', 'order')
    search_fields = ('question_text', 'assessment__title')
    list_filter = ('assessment',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'student', 'submitted_at', 'marks_obtained')
    search_fields = ('student__username', 'question__question_text')
    list_filter = ('submitted_at', 'marks_obtained')
