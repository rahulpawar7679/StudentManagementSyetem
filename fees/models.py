from django.db import models
from students.models import Student

class FeePayment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_records')
    title = models.CharField(max_length=200, help_text="e.g., Semester 1 Tuition Fee")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.student.roll_number} - {self.title} - ₹{self.amount} ({self.status})"