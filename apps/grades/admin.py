from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'grade', 'points', 'graded_by', 'graded_at')
    search_fields = ('enrollment__student__username', 'enrollment__course__code', 'grade')
    list_filter = ('grade', 'graded_at')
