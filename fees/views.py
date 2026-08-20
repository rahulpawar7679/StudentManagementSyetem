from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import FeePayment
from students.models import Student

@login_required
def fee_receipt_view(request, fee_id):
    # Allow students to view their own receipt; admins/faculty can view all
    if request.user.role == 'STUDENT' and hasattr(request.user, 'student_profile'):
        fee = get_object_or_404(FeePayment, id=fee_id, student=request.user.student_profile, status=FeePayment.Status.PAID)
    elif request.user.role in ['ADMIN', 'FACULTY'] or request.user.is_staff:
        fee = get_object_or_404(FeePayment, id=fee_id, status=FeePayment.Status.PAID)
    else:
        messages.error(request, "Receipt access denied or fee unpaid.")
        return redirect('dashboard')

    return render(request, 'fee_receipt.html', {'fee': fee})

@login_required
def generate_bulk_invoices_view(request):
    if request.user.role not in ['ADMIN', 'FACULTY'] and not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')

        students = Student.objects.all()
        created_count = 0

        for student in students:
            FeePayment.objects.create(
                student=student,
                title=title,
                amount=amount,
                due_date=due_date,
                status=FeePayment.Status.PENDING
            )
            created_count += 1

        messages.success(request, f"Successfully issued '{title}' invoices to {created_count} students.")
        return redirect('dashboard')

    return render(request, 'generate_invoices.html')