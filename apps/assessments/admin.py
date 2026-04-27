from django.contrib import admin
from .models import Assessment, Question, Answer


class QuestionInline(admin.TabularInline):
    model  = Question
    extra  = 1
    fields = ['order', 'question_text', 'model_answer', 'marks']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display  = ['title', 'created_by', 'course', 'assessment_type', 'due_date']
    list_filter   = ['assessment_type', 'course']
    search_fields = ['title']
    inlines       = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ['assessment', 'order', 'question_text', 'marks']
    list_filter   = ['assessment']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display    = ['student', 'question', 'ai_score', 'marks_obtained', 'status', 'submitted_at']
    list_filter     = ['status', 'question__assessment']
    search_fields   = ['student__username']
    readonly_fields = ['ai_score', 'similarity_score', 'ai_feedback', 'submitted_at']
