from django.urls import path
from .views import course_detail_view, manage_grades_view

urlpatterns = [
    path('<int:course_id>/', course_detail_view, name='course_detail'),
    path('grades/manage/', manage_grades_view, name='manage_grades'),
]