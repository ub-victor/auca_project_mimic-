from django.db import models
from django.conf import settings


class FeeItem(models.Model):
    STATUS_CHOICES = [('paid', 'Paid'), ('due', 'Due'), ('partial', 'Partial')]

    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fees')
    name       = models.CharField(max_length=100)
    amount     = models.DecimalField(max_digits=12, decimal_places=2)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='due')
    semester   = models.CharField(max_length=20, default='Sem 2')
    year       = models.CharField(max_length=10, default='2024/25')
    due_date   = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} — {self.name}: {self.status}"
