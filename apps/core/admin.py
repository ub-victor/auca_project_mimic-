from django.contrib import admin
from .models import Faculty, Department, Semester


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'dean')
    search_fields = ('name', 'description')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'head')
    search_fields = ('name', 'faculty__name')
    list_filter = ('faculty',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    search_fields = ('name',)
    list_filter = ('is_current',)
