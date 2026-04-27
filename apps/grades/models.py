from django.db import models
from django.conf import settings


class GradeRecord(models.Model):
    LETTER_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("F", "F"),
    ]

    enrollment = models.ForeignKey(
        "courses.Enrollment", on_delete=models.CASCADE, related_name="grades"
    )
    submission = models.OneToOneField(
        "assessments.Submission",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grade_record",
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="graded_records"
    )
    score = models.DecimalField(max_digits=6, decimal_places=2)
    letter_grade = models.CharField(max_length=2, choices=LETTER_CHOICES)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "submission"], name="unique_grade_per_enrollment_submission"
            )
        ]

    def __str__(self):
        return f"{self.enrollment.student} - {self.letter_grade}"
