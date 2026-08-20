from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import User
from students.models import Student
from courses.models import Course, Enrollment
from attendance.models import Attendance
from fees.models import FeePayment

class Command(BaseCommand):
    help = "Populate database with sample courses, students, attendance, and fees"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Create Courses
        course_data = [
            ("CS101", "Introduction to Computer Science", 4),
            ("CS201", "Data Structures & Algorithms", 4),
            ("CS301", "Database Management Systems", 3),
            ("CS401", "Web Development with Django", 3),
            ("CS501", "Machine Learning Fundamentals", 4),
        ]
        courses = []
        for code, name, credits in course_data:
            course, _ = Course.objects.get_or_create(
                course_code=code,
                defaults={"course_name": name, "credits": credits, "description": f"Learn core concepts of {name}"}
            )
            courses.append(course)

        # 2. Create Sample Student User
        email = "student@example.com"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": "student_demo",
                "first_name": "Rahul",
                "last_name": "Pawar",
                "role": User.Role.STUDENT,
                "is_active": True,
            }
        )
        if created:
            user.set_password("student123")
            user.save()

        # 3. Create Student Profile
        student, _ = Student.objects.get_or_create(
            user=user,
            defaults={
                "roll_number": "STU-2026-001",
                "department": "Computer Science & Engineering",
                "phone_number": "+91 9876543210",
                "address": "Pune, Maharashtra",
            }
        )

        # 4. Enroll in First 3 Courses
        for course in courses[:3]:
            Enrollment.objects.get_or_create(student=student, course=course)

        # 5. Create Attendance Records for Past 7 Days
        today = timezone.now().date()
        for i in range(7):
            record_date = today - timedelta(days=i)
            for enrollment in student.enrollments.all():
                Attendance.objects.get_or_create(
                    student=student,
                    course=enrollment.course,
                    date=record_date,
                    defaults={
                        "status": random.choice([Attendance.Status.PRESENT, Attendance.Status.PRESENT, Attendance.Status.ABSENT]),
                        "remarks": "Regular Lecture"
                    }
                )

        # 6. Create Sample Fee Payments
        FeePayment.objects.get_or_create(
            student=student,
            title="Semester 1 Tuition Fee",
            defaults={
                "amount": 25000.00,
                "due_date": today + timedelta(days=30),
                "status": FeePayment.Status.PENDING,
            }
        )
        FeePayment.objects.get_or_create(
            student=student,
            title="Library & Lab Deposit",
            defaults={
                "amount": 5000.00,
                "due_date": today - timedelta(days=15),
                "paid_date": today - timedelta(days=10),
                "status": FeePayment.Status.PAID,
                "transaction_id": "TXN-DEMO1234",
            }
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
        self.stdout.write(f"Student Login: {email} | Password: student123")