from django.contrib import admin
from .models import FeeStructure, Payment, StudentInvoice


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "amount", "is_mandatory")
    list_filter = ("is_mandatory", "course")
    search_fields = ("name", "course__code", "course__title")


@admin.register(StudentInvoice)
class StudentInvoiceAdmin(admin.ModelAdmin):
    list_display = ("student", "fee", "semester", "academic_year", "amount_due", "amount_paid", "status")
    list_filter = ("status", "semester", "academic_year")
    search_fields = ("student__username", "student__email", "fee__name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "method", "transaction_ref", "paid_at", "recorded_by")
    list_filter = ("method", "paid_at")
    search_fields = ("invoice__student__username", "transaction_ref", "recorded_by__username")
