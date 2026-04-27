from django.contrib import admin
from .models import Course, Department, Enrollment, TimetableSlot


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "department", "credits")
    list_filter = ("department",)
    search_fields = ("code", "title", "department__name")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "semester", "academic_year", "status")
    list_filter = ("status", "semester", "academic_year")
    search_fields = ("student__username", "student__email", "course__code", "course__title")


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ("course", "day", "start_time", "end_time", "room")
    list_filter = ("day", "course")
    search_fields = ("course__code", "course__title", "room")
