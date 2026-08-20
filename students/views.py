import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .models import Student
from .forms import StudentProfileUpdateForm
from courses.models import Course, Enrollment, Grade
from attendance.models import Attendance
from fees.models import FeePayment


@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}

    # 1. Staff / Admin Branch
    if user.is_staff or user.role in ['ADMIN', 'FACULTY']:
        all_students = Student.objects.select_related('user').all().order_by('-id')
        context['total_students'] = all_students.count()
        context['total_courses'] = Course.objects.count()
        context['total_fees_collected'] = FeePayment.objects.filter(status=FeePayment.Status.PAID).count()
        context['all_students'] = all_students
        context['student'] = None

    # 2. Student Branch
    else:
        student, _ = Student.objects.get_or_create(
            user=user,
            defaults={'roll_number': f"STU-{user.id:04d}", 'department': 'Computer Science'}
        )
        context['student'] = student
        context['enrollments'] = student.enrollments.select_related('course').all()
        context['available_courses'] = Course.objects.exclude(enrollments__student=student)
        
        # Attendance calculation
        attendance_qs = student.attendance_records.select_related('course').order_by('-date')
        total_attendance = attendance_qs.count()
        present_count = attendance_qs.filter(status=Attendance.Status.PRESENT).count()
        
        context['attendance_records'] = attendance_qs
        context['total_attendance'] = total_attendance
        context['present_count'] = present_count
        context['attendance_pct'] = round((present_count / total_attendance * 100), 1) if total_attendance > 0 else 0
        
        # Fees records
        context['fees'] = student.fee_records.order_by('due_date')

        # Grades & GPA calculation
        grades_qs = student.grades.select_related('course').all()
        context['grades'] = grades_qs

        grade_points = {'A+': 10, 'A': 9, 'B+': 8, 'B': 7, 'C': 6, 'F': 0}
        total_points = sum(grade_points.get(g.grade_letter, 0) * g.course.credits for g in grades_qs)
        total_credits = sum(g.course.credits for g in grades_qs)
        context['gpa'] = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    return render(request, 'dashboard.html', context)


@login_required
def enroll_course_view(request, course_id):
    if request.method == 'POST' and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        course = get_object_or_404(Course, id=course_id)

        enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
        if created:
            messages.success(request, f"Successfully enrolled in {course.course_name} ({course.course_code})!")
        else:
            messages.warning(request, f"You are already enrolled in {course.course_name}.")

    return redirect('dashboard')


@login_required
def drop_course_view(request, enrollment_id):
    if request.method == 'POST' and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=student)
        course_name = enrollment.course.course_name
        enrollment.delete()
        messages.info(request, f"You have dropped {course_name}.")

    return redirect('dashboard')


@login_required
def pay_fee_view(request, fee_id):
    if request.method == 'POST' and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        fee = get_object_or_404(FeePayment, id=fee_id, student=student)

        if fee.status != FeePayment.Status.PAID:
            fee.status = FeePayment.Status.PAID
            fee.paid_date = timezone.now().date()
            fee.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
            fee.save()
            messages.success(request, f"Payment of ₹{fee.amount} for '{fee.title}' was successful! Transaction ID: {fee.transaction_id}")
        else:
            messages.info(request, "This fee has already been paid.")

    return redirect('dashboard')


@login_required
def profile_view(request):
    user = request.user
    if user.role != 'STUDENT' or not hasattr(user, 'student_profile'):
        messages.warning(request, "Only students have access to the profile settings page.")
        return redirect('dashboard')

    student = user.student_profile
    profile_form = StudentProfileUpdateForm(instance=student)
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            profile_form = StudentProfileUpdateForm(request.POST, instance=student)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile details have been updated successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please fix the errors in your profile form.")

        elif action == 'change_password':
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully!")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the password errors below.")

    return render(request, 'profile.html', {
        'student': student,
        'profile_form': profile_form,
        'password_form': password_form
    })