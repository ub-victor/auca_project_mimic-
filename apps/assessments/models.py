from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class Assignment(models.Model):
    title       = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course      = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)
    lecturer    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments_created')
    due_date    = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    assignment    = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    text          = models.TextField()
    model_answer  = models.TextField(help_text="The ideal answer used for AI evaluation")
    max_score     = models.FloatField(default=10.0)
    order         = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('graded',   'Graded'),
    ]

    question         = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submissions')
    student          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    answer_text      = models.TextField(blank=True)
    answer_file      = CloudinaryField('file', blank=True, null=True, resource_type='raw')
    submitted_at     = models.DateTimeField(auto_now_add=True)

    # AI evaluation fields
    ai_score         = models.FloatField(null=True, blank=True)
    similarity_score = models.FloatField(null=True, blank=True)
    ai_feedback      = models.TextField(blank=True)

    # Lecturer override
    final_score      = models.FloatField(null=True, blank=True)
    lecturer_feedback= models.TextField(blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    graded_by        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')

    class Meta:
        unique_together = ('question', 'student')

    def __str__(self):
        return f"{self.student.username} — {self.question}"

    def effective_score(self):
        return self.final_score if self.final_score is not None else self.ai_score
