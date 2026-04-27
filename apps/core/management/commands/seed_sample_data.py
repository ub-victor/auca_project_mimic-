from datetime import date, datetime, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.assessments.models import Assessment, Question, Submission, SubmissionAnswer
from apps.courses.models import Course, Department, Enrollment, TimetableSlot
from apps.finances.models import FeeStructure, Payment, StudentInvoice
from apps.grades.models import GradeRecord


class Command(BaseCommand):
    help = "Populate sample data for local development and admin demos."

    def handle(self, *args, **options):
        cs_department, _ = Department.objects.get_or_create(
            code="CS", defaults={"name": "Computer Science", "description": "CS faculty"}
        )

        staff_user, _ = User.objects.get_or_create(
            username="staff@auca.ac.rw",
            defaults={
                "email": "staff@auca.ac.rw",
                "first_name": "Staff",
                "last_name": "User",
                "role": "staff",
                "is_staff": True,
            },
        )
        staff_user.set_password("staff123")
        staff_user.save()

        lecturer_user, _ = User.objects.get_or_create(
            username="lecturer@auca.ac.rw",
            defaults={
                "email": "lecturer@auca.ac.rw",
                "first_name": "Lecturer",
                "last_name": "User",
                "role": "lecturer",
                "is_staff": True,
            },
        )
        lecturer_user.set_password("lecturer123")
        lecturer_user.save()

        student_user, _ = User.objects.get_or_create(
            username="student@auca.ac.rw",
            defaults={
                "email": "student@auca.ac.rw",
                "first_name": "Jean",
                "last_name": "Valentin",
                "role": "student",
                "student_id": "AUCA-2024-0312",
            },
        )
        student_user.set_password("student123")
        student_user.save()

        course, _ = Course.objects.get_or_create(
            code="CSC301",
            defaults={
                "title": "Introduction to Big Data",
                "description": "Foundations of big data processing.",
                "credits": 4,
                "department": cs_department,
            },
        )
        course.lecturers.add(lecturer_user)

        enrollment, _ = Enrollment.objects.get_or_create(
            student=student_user,
            course=course,
            semester="Semester 2",
            academic_year="2025-2026",
            defaults={"status": "active"},
        )

        TimetableSlot.objects.get_or_create(
            course=course,
            day="MON",
            start_time=time(8, 0),
            end_time=time(10, 0),
            defaults={"room": "Lab A"},
        )

        assessment, _ = Assessment.objects.get_or_create(
            course=course,
            title="Big Data Assignment 1",
            defaults={
                "description": "Short written assignment on data pipelines.",
                "assessment_type": "assignment",
                "total_marks": 100,
                "due_date": timezone.make_aware(datetime(2026, 5, 20, 23, 59)),
                "created_by": lecturer_user,
            },
        )

        question_one, _ = Question.objects.get_or_create(
            assessment=assessment,
            order=1,
            defaults={"prompt": "Explain ETL vs ELT.", "max_score": 50},
        )
        question_two, _ = Question.objects.get_or_create(
            assessment=assessment,
            order=2,
            defaults={"prompt": "List three big data storage options.", "max_score": 50},
        )

        submission, _ = Submission.objects.get_or_create(
            assessment=assessment,
            student=student_user,
            defaults={
                "status": "graded",
                "overall_answer": "Sample consolidated answer",
                "ai_score": 82.0,
                "ai_feedback": "Good work overall.",
            },
        )

        SubmissionAnswer.objects.get_or_create(
            submission=submission,
            question=question_one,
            defaults={"answer_text": "ETL transforms before load.", "score": 40},
        )
        SubmissionAnswer.objects.get_or_create(
            submission=submission,
            question=question_two,
            defaults={"answer_text": "HDFS, S3, BigQuery.", "score": 42},
        )

        GradeRecord.objects.get_or_create(
            enrollment=enrollment,
            submission=submission,
            defaults={
                "graded_by": lecturer_user,
                "score": Decimal("82.00"),
                "letter_grade": "A",
                "feedback": "Solid submission.",
            },
        )

        tuition_fee, _ = FeeStructure.objects.get_or_create(
            name="Tuition Fee",
            course=course,
            defaults={"amount": Decimal("450000.00"), "is_mandatory": True},
        )
        library_fee, _ = FeeStructure.objects.get_or_create(
            name="Library Fee",
            course=course,
            defaults={"amount": Decimal("10000.00"), "is_mandatory": True},
        )

        tuition_invoice, _ = StudentInvoice.objects.get_or_create(
            student=student_user,
            fee=tuition_fee,
            semester="Semester 2",
            academic_year="2025-2026",
            defaults={
                "amount_due": Decimal("450000.00"),
                "amount_paid": Decimal("450000.00"),
                "status": "paid",
                "due_date": date(2026, 6, 1),
            },
        )
        StudentInvoice.objects.get_or_create(
            student=student_user,
            fee=library_fee,
            semester="Semester 2",
            academic_year="2025-2026",
            defaults={
                "amount_due": Decimal("10000.00"),
                "amount_paid": Decimal("0.00"),
                "status": "due",
                "due_date": date(2026, 6, 1),
            },
        )

        Payment.objects.get_or_create(
            invoice=tuition_invoice,
            transaction_ref="TRX-AUCA-001",
            defaults={
                "recorded_by": staff_user,
                "amount": Decimal("450000.00"),
                "method": "bank",
            },
        )

        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully."))
