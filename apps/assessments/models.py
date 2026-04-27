from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from apps.courses.models import Course


class GradingScheme(models.Model):
    """Lecturer defines their own grading scale per assessment."""
    name        = models.CharField(max_length=100, default='Standard')
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grading_schemes')
    a_min       = models.FloatField(default=90, help_text='Minimum % for A')
    b_min       = models.FloatField(default=80, help_text='Minimum % for B')
    c_min       = models.FloatField(default=70, help_text='Minimum % for C')
    d_min       = models.FloatField(default=60, help_text='Minimum % for D')

    def get_letter(self, percentage):
        if percentage >= self.a_min: return 'A'
        elif percentage >= self.b_min: return 'B'
        elif percentage >= self.c_min: return 'C'
        elif percentage >= self.d_min: return 'D'
        else: return 'F'

    def __str__(self):
        return f"{self.name} (A≥{self.a_min}%, B≥{self.b_min}%, C≥{self.c_min}%, D≥{self.d_min}%)"


class Assessment(models.Model):
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('midterm', 'Midterm Exam'),
        ('final', 'Final Exam'),
        ('assignment', 'Assignment'),
    ]

    title           = models.CharField(max_length=200)
    description     = models.TextField(blank=True)
    course          = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES, default='assignment')
    total_marks     = models.PositiveIntegerField(default=100)
    due_date        = models.DateTimeField()
    created_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_assessments')
    grading_scheme  = models.ForeignKey(GradingScheme, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    passing_percentage = models.FloatField(default=50.0, help_text='Minimum % to pass')

    def __str__(self):
        return f"{self.title} ({self.course.code})"


class Question(models.Model):
    assessment    = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    model_answer  = models.TextField(help_text="Ideal answer used for AI evaluation", blank=True)
    marks         = models.PositiveIntegerField(default=10)
    order         = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class Answer(models.Model):
    STATUS_CHOICES = [('pending', 'Pending Review'), ('graded', 'Graded')]

    question          = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    student           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    answer_text       = models.TextField(blank=True)
    answer_file       = CloudinaryField('file', blank=True, null=True, resource_type='raw')
    submitted_at      = models.DateTimeField(auto_now_add=True)

    # AI evaluation (Valentin - Team 5)
    ai_score          = models.FloatField(null=True, blank=True)
    similarity_score  = models.FloatField(null=True, blank=True)
    ai_feedback       = models.TextField(blank=True)

    # Lecturer grading
    marks_obtained    = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    letter_grade      = models.CharField(max_length=3, blank=True)
    lecturer_feedback = models.TextField(blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    graded_by         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_answers')
    graded_at         = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('question', 'student')

    def __str__(self):
        return f"{self.student} - {self.question}"

    def effective_score(self):
        return float(self.marks_obtained) if self.marks_obtained is not None else self.ai_score

    def percentage(self):
        if self.marks_obtained is not None and self.question.marks > 0:
            return round(float(self.marks_obtained) / self.question.marks * 100, 1)
        return None
