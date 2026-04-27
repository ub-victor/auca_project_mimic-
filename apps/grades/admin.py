from django.contrib import admin
from .models import GradeRecord


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "submission", "score", "letter_grade", "graded_by", "graded_at")
    list_filter = ("letter_grade", "graded_at")
    search_fields = (
        "enrollment__student__username",
        "enrollment__course__code",
        "graded_by__username",
    )
