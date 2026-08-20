from django.contrib import admin
from .models import FeePayment

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'amount', 'due_date', 'status', 'paid_date', 'transaction_id')
    list_filter = ('status', 'due_date')
    search_fields = ('student__roll_number', 'student__user__email', 'title', 'transaction_id')