from django.db import models
from django.conf import settings


class Grade(models.Model):
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='grades')
    course     = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='grades')
    score      = models.FloatField()
    letter     = models.CharField(max_length=2, blank=True)
    semester   = models.CharField(max_length=20, default='Sem 2')
    year       = models.CharField(max_length=10, default='2024/25')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'semester', 'year')

    def save(self, *args, **kwargs):
        if self.score >= 90: self.letter = 'A+'
        elif self.score >= 80: self.letter = 'A'
        elif self.score >= 75: self.letter = 'B+'
        elif self.score >= 70: self.letter = 'B'
        elif self.score >= 65: self.letter = 'C+'
        elif self.score >= 60: self.letter = 'C'
        else: self.letter = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} — {self.course.code}: {self.letter}"
