from django.db import models
from django.conf import settings


class FeeStructure(models.Model):
    name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="fee_structures"
    )
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "course"], name="unique_fee_type_per_course")
        ]

    def __str__(self):
        return f"{self.name} ({self.course.code})"


class StudentInvoice(models.Model):
    STATUS_CHOICES = [
        ("due", "Due"),
        ("paid", "Paid"),
        ("partial", "Partial"),
        ("overdue", "Overdue"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invoices"
    )
    fee = models.ForeignKey(FeeStructure, on_delete=models.PROTECT, related_name="invoices")
    semester = models.CharField(max_length=30)
    academic_year = models.CharField(max_length=9)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="due")
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "fee", "semester", "academic_year"],
                name="unique_invoice_per_fee_and_term",
            )
        ]

    def __str__(self):
        return f"Invoice {self.student} - {self.fee.name}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("bank", "Bank Transfer"),
        ("mobile", "Mobile Money"),
    ]

    invoice = models.ForeignKey(
        StudentInvoice, on_delete=models.CASCADE, related_name="payments"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="recorded_payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="bank")
    transaction_ref = models.CharField(max_length=120, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice.student} paid {self.amount}"
