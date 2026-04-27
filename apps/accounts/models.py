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
        return f"{self.get_full_name() or self.username} ({self.role})"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('login',       'Login'),
        ('logout',      'Logout'),
        ('create',      'Create'),
        ('update',      'Update'),
        ('delete',      'Delete'),
        ('view',        'View'),
        ('grade',       'Grade'),
        ('enroll',      'Enroll'),
        ('impersonate', 'Impersonate'),
    ]
    user       = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action     = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target     = models.CharField(max_length=200, blank=True)
    detail     = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} — {self.action} — {self.timestamp:%Y-%m-%d %H:%M}"


class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('all',       'Everyone'),
        ('students',  'Students Only'),
        ('lecturers', 'Lecturers Only'),
    ]
    title      = models.CharField(max_length=200)
    body       = models.TextField()
    audience   = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    course     = models.ForeignKey('courses.Course', on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='announcements')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
