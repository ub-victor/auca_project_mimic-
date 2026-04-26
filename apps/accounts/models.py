from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student',  'Student'),
        ('lecturer', 'Lecturer'),
        ('staff',    'Staff'),
    ]

    role            = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    student_id      = models.CharField(max_length=30, blank=True, null=True)
    bio             = models.TextField(blank=True)
    phone           = models.CharField(max_length=20, blank=True)
    profile_picture = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
