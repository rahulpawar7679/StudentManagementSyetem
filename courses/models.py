import os
from django.db import models
from django.conf import settings
from students.models import Student


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_code}: {self.course_name}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        DROPPED = 'DROPPED', 'Dropped'
        COMPLETED = 'COMPLETED', 'Completed'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.roll_number} -> {self.course.course_code} ({self.status})"


class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.course_code} - {self.title}"

    @property
    def file_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()


class Grade(models.Model):
    class Letter(models.TextChoices):
        A_PLUS = 'A+', 'A+'
        A = 'A', 'A'
        B_PLUS = 'B+', 'B+'
        B = 'B', 'B'
        C = 'C', 'C'
        F = 'F', 'F'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    grade_letter = models.CharField(max_length=3, choices=Letter.choices, default=Letter.B)
    semester = models.CharField(max_length=20, default='Semester 1')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course', 'semester')

    def __str__(self):
        return f"{self.student.roll_number} - {self.course.course_code}: {self.grade_letter}"