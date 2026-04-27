from django.contrib import admin
from .models import Assignment, Question, Submission


class QuestionInline(admin.TabularInline):
    model  = Question
    extra  = 1
    fields = ['order', 'text', 'model_answer', 'max_score']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display  = ['title', 'lecturer', 'course', 'due_date', 'created_at']
    list_filter   = ['lecturer', 'course']
    search_fields = ['title']
    inlines       = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ['assignment', 'order', 'text', 'max_score']
    list_filter   = ['assignment']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display  = ['student', 'question', 'ai_score', 'final_score', 'status', 'submitted_at']
    list_filter   = ['status', 'question__assignment']
    search_fields = ['student__username']
    readonly_fields = ['ai_score', 'similarity_score', 'ai_feedback', 'submitted_at']
