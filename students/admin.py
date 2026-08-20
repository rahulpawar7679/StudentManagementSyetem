from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'get_full_name', 'department', 'phone_number', 'created_at')
    search_fields = ('roll_number', 'user__email', 'user__first_name', 'user__last_name', 'department')
    list_filter = ('department',)

    @admin.display(description='Student Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.email