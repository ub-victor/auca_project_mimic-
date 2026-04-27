from django.db import models
from django.conf import settings
from apps.courses.models import CourseEnrollment


class Grade(models.Model):
    GRADE_CHOICES = [
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('C-', 'C-'),
        ('D+', 'D+'),
        ('D', 'D'),
        ('F', 'F'),
    ]

    enrollment = models.OneToOneField(CourseEnrollment, on_delete=models.CASCADE, related_name='detailed_grade')
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES)
    points = models.DecimalField(max_digits=3, decimal_places=2)  # GPA points
    remarks = models.TextField(blank=True)
    graded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='graded_grades')
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enrollment} - {self.grade}"
