from django.db import models
from django.conf import settings


class Assessment(models.Model):
    TYPE_CHOICES = [
        ("assignment", "Assignment"),
        ("quiz", "Quiz"),
        ("exam", "Exam"),
    ]

    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="assessments"
    )
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="assignment")
    total_marks = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_assessments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.course.code}: {self.title}"


class Question(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="questions"
    )
    prompt = models.TextField()
    max_score = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "order"], name="unique_question_order_per_assessment"
            )
        ]

    def __str__(self):
        return f"{self.assessment.title} Q{self.order}"


class Submission(models.Model):
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("graded", "Graded"),
        ("late", "Late"),
    ]

    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    overall_answer = models.TextField(blank=True)
    file_url = models.URLField(blank=True)
    ai_score = models.FloatField(blank=True, null=True)
    ai_feedback = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "student"], name="unique_submission_per_assessment"
            )
        ]

    def __str__(self):
        return f"{self.student} -> {self.assessment}"


class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    answer_text = models.TextField(blank=True)
    score = models.FloatField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["submission", "question"], name="unique_answer_per_question"
            )
        ]

    def __str__(self):
        return f"Answer by {self.submission.student} for {self.question}"
