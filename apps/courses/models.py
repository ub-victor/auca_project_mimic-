from django.db import models
from django.conf import settings


class Course(models.Model):
    code        = models.CharField(max_length=20, unique=True)
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credits     = models.PositiveIntegerField(default=3)
    lecturer    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} — {self.title}"


class Enrollment(models.Model):
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} → {self.course.code}"
