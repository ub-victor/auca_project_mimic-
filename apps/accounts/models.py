from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from cloudinary.models import CloudinaryField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    STUDENT  = 'student'
    LECTURER = 'lecturer'
    STAFF    = 'staff'

    ROLE_CHOICES = [
        (STUDENT,  'Student'),
        (LECTURER, 'Lecturer'),
        (STAFF,    'Staff'),
    ]

    username        = None
    email           = models.EmailField(unique=True)
    student_id      = models.CharField(max_length=20, unique=True, blank=True, null=True)
    role            = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    bio             = models.TextField(blank=True, null=True)
    profile_picture = CloudinaryField('profile_picture', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
