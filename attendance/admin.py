from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'student', 'course', 'status', 'remarks')
    list_filter = ('status', 'date', 'course')
    search_fields = ('student__roll_number', 'student__user__email', 'course__course_code')
    date_hierarchy = 'date'