from django.db import models
from django.conf import settings


class Faculty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    dean = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='dean_of')

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    head = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='head_of')

    class Meta:
        unique_together = ('name', 'faculty')

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"


class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Fall 2024", "Spring 2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.name
