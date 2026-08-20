from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'course_name', 'credits', 'created_at')
    search_fields = ('course_code', 'course_name')
    list_filter = ('credits',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date', 'status')
    list_filter = ('status', 'enrollment_date', 'course')
    search_fields = ('student__roll_number', 'student__user__email', 'course__course_code', 'course__course_name')