from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    credits = models.PositiveSmallIntegerField(default=3)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="courses"
    )
    lecturers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="taught_courses", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("dropped", "Dropped"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    semester = models.CharField(max_length=30)
    academic_year = models.CharField(max_length=9)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "semester", "academic_year"],
                name="unique_enrollment_per_term",
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.course} ({self.semester} {self.academic_year})"


class TimetableSlot(models.Model):
    DAY_CHOICES = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="timetable_slots")
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.course.code} {self.day} {self.start_time}-{self.end_time}"
