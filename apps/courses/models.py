from django.db import models
from django.conf import settings
from apps.core.models import Department, Semester


class Course(models.Model):
    code        = models.CharField(max_length=20, unique=True)
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits     = models.PositiveIntegerField()
    department  = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    lecturer    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught')
    semester    = models.ManyToManyField(Semester, related_name='courses')

    def __str__(self):
        return f"{self.code} - {self.title}"


class CourseEnrollment(models.Model):
    student         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    semester        = models.ForeignKey(Semester, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    grade           = models.CharField(max_length=5, blank=True)

    class Meta:
        unique_together = ('student', 'course', 'semester')

    def __str__(self):
        return f"{self.student} - {self.course} ({self.semester})"
