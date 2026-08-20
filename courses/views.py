from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment, CourseMaterial, Grade


@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    
    is_enrolled = False
    if user.role == 'STUDENT' and hasattr(user, 'student_profile'):
        is_enrolled = Enrollment.objects.filter(course=course, student=user.student_profile).exists()
    elif user.role in ['ADMIN', 'FACULTY'] or user.is_staff:
        is_enrolled = True

    if not is_enrolled:
        messages.error(request, "You must be enrolled in this course to view syllabus materials.")
        return redirect('dashboard')

    if request.method == 'POST' and (user.role in ['ADMIN', 'FACULTY'] or user.is_staff):
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        uploaded_file = request.FILES.get('file')

        if title and uploaded_file:
            CourseMaterial.objects.create(
                course=course,
                title=title,
                description=description,
                file=uploaded_file
            )
            messages.success(request, f"Document '{title}' uploaded successfully.")
            return redirect('course_detail', course_id=course.id)
        else:
            messages.error(request, "Please provide a valid title and file.")

    materials = course.materials.order_by('-uploaded_at')
    return render(request, 'course_detail.html', {
        'course': course,
        'materials': materials,
        'can_upload': user.role in ['ADMIN', 'FACULTY'] or user.is_staff
    })


@login_required
def manage_grades_view(request):
    if request.user.role not in ['ADMIN', 'FACULTY'] and not request.user.is_staff:
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard')

    courses = Course.objects.all()
    selected_course_id = request.GET.get('course_id') or (courses.first().id if courses.exists() else None)
    selected_course = None
    student_rows = []

    if selected_course_id:
        selected_course = get_object_or_404(Course, id=selected_course_id)
        enrollments = Enrollment.objects.filter(
            course=selected_course,
            status=Enrollment.Status.ACTIVE
        ).select_related('student__user')

        grades_map = {
            g.student_id: g
            for g in Grade.objects.filter(course=selected_course)
        }

        for enrollment in enrollments:
            student = enrollment.student
            existing_grade = grades_map.get(student.id)
            student_rows.append({
                'student': student,
                'marks': existing_grade.marks_obtained if existing_grade else '',
                'grade_letter': existing_grade.grade_letter if existing_grade else 'B'
            })

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        semester = request.POST.get('semester', 'Semester 1')
        course = get_object_or_404(Course, id=course_id)
        enrollments = Enrollment.objects.filter(course=course, status=Enrollment.Status.ACTIVE)

        for enrollment in enrollments:
            student = enrollment.student
            marks = request.POST.get(f"marks_{student.id}", 0)
            letter = request.POST.get(f"grade_{student.id}", 'B')

            Grade.objects.update_or_create(
                student=student,
                course=course,
                semester=semester,
                defaults={
                    'marks_obtained': marks or 0.0,
                    'grade_letter': letter
                }
            )
        messages.success(request, f"Grades updated successfully for {course.course_code}!")
        return redirect(f"{request.path}?course_id={course_id}")

    return render(request, 'manage_grades.html', {
        'courses': courses,
        'selected_course': selected_course,
        'student_rows': student_rows,
    })