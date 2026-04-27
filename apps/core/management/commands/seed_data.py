from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import CustomUser
from apps.core.models import Faculty, Department, Semester
from apps.courses.models import Course, CourseEnrollment
from apps.assessments.models import Assessment, Question


class Command(BaseCommand):
    help = 'Seed sample data for all users'

    def handle(self, *args, **kwargs):
        student  = CustomUser.objects.filter(role='student').first()
        lecturer = CustomUser.objects.filter(role='lecturer').first()

        # Core: Faculty, Department, Semester
        faculty, _ = Faculty.objects.get_or_create(name='Faculty of Science & Technology')
        dept, _    = Department.objects.get_or_create(name='Computer Science', defaults={'faculty': faculty})
        semester, _= Semester.objects.get_or_create(name='Sem 2 2024/25', defaults={
            'start_date': '2025-01-15', 'end_date': '2025-06-30', 'is_current': True
        })

        # Courses
        courses_data = [
            ('CS301', 'Intro to Big Data', 3),
            ('CS302', 'Web Development', 3),
            ('CS303', 'Database Systems', 3),
            ('CS304', 'Data Structures', 4),
            ('CS305', 'Software Engineering', 3),
        ]
        courses = []
        for code, title, credits in courses_data:
            c, _ = Course.objects.get_or_create(code=code, defaults={
                'title': title, 'credits': credits,
                'lecturer': lecturer, 'department': dept
            })
            c.semester.add(semester)
            courses.append(c)

        # Enroll student
        if student:
            for c in courses:
                CourseEnrollment.objects.get_or_create(student=student, course=c, semester=semester)

        # Assignments from lecturer
        if lecturer:
            a1, c1 = Assessment.objects.get_or_create(
                title='Introduction to Machine Learning',
                created_by=lecturer,
                defaults={
                    'description': 'Answer the following ML questions.',
                    'course': courses[0], 'assessment_type': 'assignment',
                    'total_marks': 30,
                    'due_date': timezone.now() + timezone.timedelta(days=7)
                }
            )
            if c1:
                Question.objects.create(assessment=a1, order=1, marks=10,
                    question_text='What is supervised learning? Give two examples.',
                    model_answer='Supervised learning trains models on labeled data. Examples: linear regression for house prices, classification for spam detection.')
                Question.objects.create(assessment=a1, order=2, marks=10,
                    question_text='Explain overfitting vs underfitting.',
                    model_answer='Overfitting: model memorizes training noise, fails on new data. Underfitting: model too simple to capture patterns.')
                Question.objects.create(assessment=a1, order=3, marks=10,
                    question_text='What is a neural network?',
                    model_answer='A neural network is a computational model inspired by the brain with layers of interconnected nodes that learn patterns from data.')

            a2, c2 = Assessment.objects.get_or_create(
                title='Web Development Fundamentals',
                created_by=lecturer,
                defaults={
                    'description': 'Answer questions about web development.',
                    'course': courses[1], 'assessment_type': 'assignment',
                    'total_marks': 20,
                    'due_date': timezone.now() + timezone.timedelta(days=14)
                }
            )
            if c2:
                Question.objects.create(assessment=a2, order=1, marks=10,
                    question_text='What is the difference between GET and POST HTTP methods?',
                    model_answer='GET retrieves data, parameters visible in URL. POST sends data in request body, used for forms and sensitive data.')
                Question.objects.create(assessment=a2, order=2, marks=10,
                    question_text='Explain Django MVT architecture.',
                    model_answer='MVT: Model handles data/database, View contains business logic, Template handles HTML presentation.')

        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully!'))
