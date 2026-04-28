from django.contrib import admin
from .models import Assessment, Question, Answer, Submission


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


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'student', 'status', 'ai_score', 'similarity_score', 'final_grade', 'graded_at')
    search_fields = ('student__username', 'assessment__title')
    list_filter = ('status', 'assessment', 'graded_at')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'student', 'submitted_at', 'marks_obtained')
    search_fields = ('student__username', 'question__question_text')
    list_filter = ('submitted_at', 'marks_obtained')
