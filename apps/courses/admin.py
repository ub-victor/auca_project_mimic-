from django.contrib import admin
from .models import Course, CourseEnrollment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'lecturer', 'credits')
    search_fields = ('code', 'title', 'department__name')
    list_filter = ('department', 'lecturer')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'grade', 'enrollment_date')
    search_fields = ('student__username', 'course__code', 'course__title')
    list_filter = ('semester', 'grade')
