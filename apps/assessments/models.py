from django.db import models
from django.conf import settings
from apps.courses.models import Course


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm Exam'),
        ('final', 'Final Exam'),
        ('assignment', 'Assignment'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    total_marks = models.PositiveIntegerField()
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assessments')

    def __str__(self):
        return f"{self.title} ({self.course.code})"


class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    reference_answer = models.TextField(blank=True)
    marks = models.PositiveIntegerField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class Submission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    ai_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    final_grade = models.CharField(max_length=10, blank=True)
    lecturer_feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')

    class Meta:
        unique_together = ('assessment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student} - {self.assessment.title}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(blank=True)
    answer_file = models.FileField(upload_to='assessment_answers/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('question', 'student')

    def __str__(self):
        return f"{self.student} - {self.question}"
