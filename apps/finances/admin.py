from django.contrib import admin
from .models import Fee, Payment


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_type', 'amount', 'due_date', 'is_paid', 'semester')
    search_fields = ('student__username', 'fee_type')
    list_filter = ('fee_type', 'is_paid', 'semester')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'payment_date', 'reference')
    search_fields = ('student__username', 'reference')
    list_filter = ('payment_date',)
