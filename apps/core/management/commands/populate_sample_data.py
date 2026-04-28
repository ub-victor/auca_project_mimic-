from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import Faculty, Department, Semester
from apps.courses.models import Course, CourseEnrollment
from apps.assessments.models import Assessment, Question, Answer
from apps.finances.models import Fee, Payment
from apps.grades.models import Grade
from datetime import date, datetime
from decimal import Decimal

User = get_user_model()

# Demo passwords are intentionally simple for local development only.
# In production, use environment variables or Django's createsuperuser.
_DEMO_PASSWORD = 'changeme_in_production'


class Command(BaseCommand):
    help = 'Populate sample data for the AUCA portal'

    def handle(self, *args, **options):
        self.stdout.write('Populating sample data...')

        student, _ = User.objects.get_or_create(
            username='student@auca.ac.rw',
            defaults={
                'email': 'student@auca.ac.rw',
                'first_name': 'John', 'last_name': 'Doe',
                'role': 'student', 'student_id': 'AUCA-2024-001',
            }
        )
        student.set_password(_DEMO_PASSWORD)
        student.save()

        lecturer, _ = User.objects.get_or_create(
            username='lecturer@auca.ac.rw',
            defaults={
                'email': 'lecturer@auca.ac.rw',
                'first_name': 'Jane', 'last_name': 'Smith',
                'role': 'lecturer',
            }
        )
        lecturer.set_password(_DEMO_PASSWORD)
        lecturer.save()

        staff, _ = User.objects.get_or_create(
            username='staff@auca.ac.rw',
            defaults={
                'email': 'staff@auca.ac.rw',
                'first_name': 'Admin', 'last_name': 'User',
                'role': 'staff',
            }
        )
        staff.set_password(_DEMO_PASSWORD)
        staff.save()

        faculty, _ = Faculty.objects.get_or_create(
            name='Faculty of Science and Technology',
            defaults={'description': 'FST'}
        )
        department, _ = Department.objects.get_or_create(
            name='Computer Science',
            defaults={'faculty': faculty, 'head': lecturer}
        )
        semester, _ = Semester.objects.get_or_create(
            name='Fall 2024',
            defaults={
                'start_date': date(2024, 9, 1),
                'end_date': date(2024, 12, 31),
                'is_current': True
            }
        )

        course, _ = Course.objects.get_or_create(
            code='CS101',
            defaults={
                'title': 'Introduction to Programming',
                'description': 'Basic programming concepts',
                'credits': 3,
                'department': department,
                'lecturer': lecturer,
            }
        )
        course.semester.add(semester)

        enrollment, _ = CourseEnrollment.objects.get_or_create(
            student=student, course=course, semester=semester
        )

        assessment, _ = Assessment.objects.get_or_create(
            title='Midterm Quiz',
            created_by=lecturer,
            defaults={
                'description': 'Programming basics quiz',
                'course': course,
                'assessment_type': 'quiz',
                'total_marks': 20,
                'due_date': datetime(2024, 10, 15, 23, 59),
            }
        )

        question, _ = Question.objects.get_or_create(
            assessment=assessment, order=1,
            defaults={'question_text': 'What is a variable?', 'marks': 5}
        )

        Answer.objects.get_or_create(
            question=question, student=student,
            defaults={
                'answer_text': 'A variable is a storage location with a name.',
                'marks_obtained': Decimal('4.5')
            }
        )

        fee, _ = Fee.objects.get_or_create(
            student=student, fee_type='tuition', semester=semester,
            defaults={
                'amount': Decimal('450000.00'),
                'due_date': date(2024, 9, 30),
                'is_paid': True,
            }
        )

        if not Payment.objects.filter(reference='PAY-001').exists():
            payment = Payment.objects.create(
                student=student,
                amount=Decimal('450000.00'),
                reference='PAY-001'
            )
            payment.fees.add(fee)

        Grade.objects.get_or_create(
            enrollment=enrollment,
            defaults={
                'grade': 'A', 'points': Decimal('4.0'),
                'remarks': 'Excellent work', 'graded_by': lecturer
            }
        )

        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))
