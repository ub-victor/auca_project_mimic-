from django.contrib import admin
from .models import Course, CourseEnrollment, CourseSchedule


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'department', 'lecturer', 'credits')
    search_fields = ('code', 'title', 'department__name')
    list_filter = ('department', 'lecturer')
    filter_horizontal = ('semester',)


@admin.register(CourseSchedule)
class CourseScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'day_of_week', 'start_time', 'end_time', 'room')
    search_fields = ('course__code', 'course__title', 'room')
    list_filter = ('semester', 'day_of_week')


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'grade', 'enrollment_date')
    search_fields = ('student__username', 'course__code', 'course__title')
    list_filter = ('semester', 'grade')
