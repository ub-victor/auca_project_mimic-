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

class Command(BaseCommand):
    help = 'Populate sample data for the AUCA portal'

    def handle(self, *args, **options):
        self.stdout.write('Populating sample data...')

        # Create users
        student = User.objects.create_user(
            username='student@auca.ac.rw',
            email='student@auca.ac.rw',
            password='student123',
            first_name='John',
            last_name='Doe',
            role='student',
            student_id='AUCA-2024-001'
        )

        lecturer = User.objects.create_user(
            username='lecturer@auca.ac.rw',
            email='lecturer@auca.ac.rw',
            password='lecturer123',
            first_name='Jane',
            last_name='Smith',
            role='lecturer'
        )

        staff = User.objects.create_user(
            username='staff@auca.ac.rw',
            email='staff@auca.ac.rw',
            password='staff123',
            first_name='Admin',
            last_name='User',
            role='staff'
        )

        # Core data
        faculty = Faculty.objects.create(name='Faculty of Science and Technology', description='FST')
        department = Department.objects.create(name='Computer Science', faculty=faculty, head=lecturer)
        semester = Semester.objects.create(
            name='Fall 2024',
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 31),
            is_current=True
        )

        # Courses
        course = Course.objects.create(
            code='CS101',
            title='Introduction to Programming',
            description='Basic programming concepts',
            credits=3,
            department=department,
            lecturer=lecturer
        )
        course.semester.add(semester)

        # Enrollment
        enrollment = CourseEnrollment.objects.create(
            student=student,
            course=course,
            semester=semester
        )

        # Assessment
        assessment = Assessment.objects.create(
            title='Midterm Quiz',
            description='Programming basics quiz',
            course=course,
            assessment_type='quiz',
            total_marks=20,
            due_date=datetime(2024, 10, 15, 23, 59),
            created_by=lecturer
        )

        question = Question.objects.create(
            assessment=assessment,
            question_text='What is a variable?',
            marks=5,
            order=1
        )

        answer = Answer.objects.create(
            question=question,
            student=student,
            answer_text='A variable is a storage location with a name.',
            marks_obtained=Decimal('4.5')
        )

        # Finances
        fee = Fee.objects.create(
            student=student,
            fee_type='tuition',
            amount=Decimal('450000.00'),
            due_date=date(2024, 9, 30),
            is_paid=True,
            semester=semester
        )

        payment = Payment.objects.create(
            student=student,
            amount=Decimal('450000.00'),
            reference='PAY-001'
        )
        payment.fees.add(fee)

        # Grades
        grade = Grade.objects.create(
            enrollment=enrollment,
            grade='A',
            points=Decimal('4.0'),
            remarks='Excellent work',
            graded_by=lecturer
        )

        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))