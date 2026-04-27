from django.db import models
from django.conf import settings


class Fee(models.Model):
    FEE_TYPES = [
        ('tuition', 'Tuition Fee'),
        ('registration', 'Registration Fee'),
        ('library', 'Library Fee'),
        ('ict', 'ICT Fee'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fees')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    semester = models.ForeignKey('core.Semester', on_delete=models.CASCADE, related_name='fees')

    def __str__(self):
        return f"{self.student} - {self.get_fee_type_display()} - {self.amount}"


class Payment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)
    fees = models.ManyToManyField(Fee, related_name='payments')  # Many-to-many for partial payments

    def __str__(self):
        return f"{self.student} - {self.amount} - {self.reference}"
