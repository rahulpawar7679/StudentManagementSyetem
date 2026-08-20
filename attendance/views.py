from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from courses.models import Course, Enrollment
from students.models import Student
from .models import Attendance

@login_required
def mark_attendance_view(request):
    # Ensure user has staff, admin, or faculty privileges
    if request.user.role not in ['ADMIN', 'FACULTY'] and not request.user.is_staff:
        messages.error(request, "Unauthorized. Only faculty/administrators can mark attendance.")
        return redirect('dashboard')

    courses = Course.objects.all()
    selected_course_id = request.GET.get('course_id') or (courses.first().id if courses.exists() else None)
    selected_date = request.GET.get('date') or str(timezone.now().date())

    selected_course = None
    enrollments = []

    if selected_course_id:
        selected_course = get_object_or_404(Course, id=selected_course_id)
        enrollments = Enrollment.objects.filter(
            course=selected_course,
            status=Enrollment.Status.ACTIVE
        ).select_related('student__user')

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        attendance_date = request.POST.get('date')
        course = get_object_or_404(Course, id=course_id)

        for enrollment in enrollments:
            student = enrollment.student
            status_key = f"status_{student.id}"
            status_value = request.POST.get(status_key, Attendance.Status.ABSENT)

            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=attendance_date,
                defaults={'status': status_value}
            )

        messages.success(request, f"Attendance saved for {course.course_code} on {attendance_date}!")
        return redirect(f"{request.path}?course_id={course_id}&date={attendance_date}")

    # Fetch existing records for this session to pre-fill the form
    existing_attendance = {}
    if selected_course:
        records = Attendance.objects.filter(course=selected_course, date=selected_date)
        for rec in records:
            existing_attendance[rec.student_id] = rec.status

    context = {
        'courses': courses,
        'selected_course': selected_course,
        'selected_date': selected_date,
        'enrollments': enrollments,
        'existing_attendance': existing_attendance,
    }
    return render(request, 'mark_attendance.html', context)