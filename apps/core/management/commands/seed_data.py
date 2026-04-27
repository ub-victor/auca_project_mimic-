from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser
from apps.courses.models import Course, Enrollment
from apps.grades.models import Grade
from apps.finances.models import FeeItem
from apps.assessments.models import Assignment, Question


class Command(BaseCommand):
    help = 'Seed sample data for all users'

    def handle(self, *args, **kwargs):
        # Fix user names
        student = CustomUser.objects.filter(role='student').first()
        lecturer = CustomUser.objects.filter(role='lecturer').first()
        staff = CustomUser.objects.filter(role='staff').first()

        if student:
            student.first_name = 'Jean'; student.last_name = 'Valentin'
            student.student_id = 'AUCA-2024-0312'; student.save()

        if lecturer:
            lecturer.first_name = 'Prof'; lecturer.last_name = 'Mutijima'; lecturer.save()

        if staff:
            staff.first_name = 'Admin'; staff.last_name = 'Staff'; staff.save()

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
            c, _ = Course.objects.get_or_create(code=code, defaults={'title': title, 'credits': credits, 'lecturer': lecturer})
            courses.append(c)

        # Enroll student + grades + fees
        if student:
            for c in courses:
                Enrollment.objects.get_or_create(student=student, course=c)
            for c, score in zip(courses, [85, 78, 92, 70, 88]):
                Grade.objects.get_or_create(student=student, course=c, semester='Sem 2', year='2024/25', defaults={'score': score})
            for name, amount, status in [
                ('Tuition Fee', 450000, 'paid'),
                ('Registration Fee', 25000, 'paid'),
                ('Library Fee', 10000, 'due'),
                ('ICT Fee', 15000, 'due'),
            ]:
                FeeItem.objects.get_or_create(student=student, name=name, semester='Sem 2', year='2024/25', defaults={'amount': amount, 'status': status})

        # Assignment from lecturer
        if lecturer:
            a, created = Assignment.objects.get_or_create(
                title='Introduction to Machine Learning',
                lecturer=lecturer,
                defaults={'description': 'Answer the following ML questions.', 'course': courses[0]}
            )
            if created:
                Question.objects.create(assignment=a, order=1, max_score=10,
                    text='What is supervised learning? Give two examples.',
                    model_answer='Supervised learning trains models on labeled data. Examples: linear regression for house prices, classification for spam detection.')
                Question.objects.create(assignment=a, order=2, max_score=10,
                    text='Explain overfitting vs underfitting.',
                    model_answer='Overfitting: model memorizes training noise, fails on new data. Underfitting: model too simple to capture patterns.')
                Question.objects.create(assignment=a, order=3, max_score=10,
                    text='What is a neural network?',
                    model_answer='A neural network is a computational model inspired by the brain with layers of interconnected nodes that learn patterns from data.')

            a2, created2 = Assignment.objects.get_or_create(
                title='Web Development Fundamentals',
                lecturer=lecturer,
                defaults={'description': 'Answer questions about web development.', 'course': courses[1]}
            )
            if created2:
                Question.objects.create(assignment=a2, order=1, max_score=10,
                    text='What is the difference between GET and POST HTTP methods?',
                    model_answer='GET retrieves data from the server and parameters are visible in the URL. POST sends data to the server in the request body, used for forms and sensitive data.')
                Question.objects.create(assignment=a2, order=2, max_score=10,
                    text='Explain what Django MVT architecture means.',
                    model_answer='MVT stands for Model-View-Template. Model handles data and database, View contains business logic, Template handles presentation/HTML rendering.')

        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully!'))
