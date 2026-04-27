import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import CustomUser
from apps.core.models import Faculty, Department, Semester
from apps.courses.models import Course, CourseEnrollment
from apps.assessments.models import Assessment, Question, Answer
from apps.finances.models import Fee
from apps.grades.models import Grade


STUDENT_DATA = [
    ('Jean', 'Valentin',   'jean.valentin'),
    ('Marie', 'Uwase',     'marie.uwase'),
    ('Eric', 'Nkurunziza', 'eric.nkurunziza'),
    ('Grace', 'Mukamana',  'grace.mukamana'),
    ('Patrick', 'Habimana','patrick.habimana'),
    ('Diane', 'Ingabire',  'diane.ingabire'),
    ('Claude', 'Bizimana', 'claude.bizimana'),
    ('Ange', 'Uwimana',    'ange.uwimana'),
    ('Kevin', 'Ndayishimiye','kevin.ndayishimiye'),
    ('Solange', 'Mukeshimana','solange.mukeshimana'),
    ('Thierry', 'Niyonzima','thierry.niyonzima'),
    ('Clarisse', 'Umubyeyi','clarisse.umubyeyi'),
    ('Fabrice', 'Nshimiyimana','fabrice.nshimiyimana'),
    ('Josiane', 'Uwera',   'josiane.uwera'),
    ('Alexis', 'Hakizimana','alexis.hakizimana'),
    ('Sandrine', 'Mukamurenzi','sandrine.mukamurenzi'),
    ('Olivier', 'Niyomugabo','olivier.niyomugabo'),
    ('Vestine', 'Mukagasana','vestine.mukagasana'),
    ('Innocent', 'Nzeyimana','innocent.nzeyimana'),
    ('Chantal', 'Uwamahoro','chantal.uwamahoro'),
    ('Bosco', 'Nshuti',    'bosco.nshuti'),
    ('Deborah', 'Mutijima', 'deborah.mutijima'),
    ('Hirwa', 'Roy',       'hirwa.roy'),
    ('Clement', 'Nzabonimpa','clement.nzabonimpa'),
    ('Praise', 'Mutijima', 'praise.mutijima'),
    ('Anduru', 'Ochieng',  'anduru.ochieng'),
]

LECTURER_DATA = [
    ('Prof', 'Mutijima',   'prof.mutijima'),
    ('Dr', 'Nkurunziza',   'dr.nkurunziza'),
    ('Prof', 'Uwimana',    'prof.uwimana'),
    ('Dr', 'Habimana',     'dr.habimana'),
    ('Prof', 'Ingabire',   'prof.ingabire'),
    ('Dr', 'Bizimana',     'dr.bizimana'),
    ('Prof', 'Mukamana',   'prof.mukamana'),
    ('Dr', 'Niyonzima',    'dr.niyonzima'),
    ('Prof', 'Hakizimana', 'prof.hakizimana'),
    ('Dr', 'Nzeyimana',    'dr.nzeyimana'),
    ('Prof', 'Uwera',      'prof.uwera'),
    ('Dr', 'Nshimiyimana', 'dr.nshimiyimana'),
]

COURSES_DATA = [
    ('CS101', 'Introduction to Programming',        3),
    ('CS201', 'Data Structures & Algorithms',       4),
    ('CS301', 'Introduction to Big Data',           3),
    ('CS302', 'Web Development',                    3),
    ('CS303', 'Database Systems',                   3),
    ('CS304', 'Data Structures',                    4),
    ('CS305', 'Software Engineering',               3),
    ('CS401', 'Machine Learning',                   4),
    ('CS402', 'Artificial Intelligence',            3),
    ('CS403', 'Computer Networks',                  3),
    ('CS404', 'Operating Systems',                  3),
    ('CS405', 'Cloud Computing',                    3),
    ('CS406', 'Cybersecurity Fundamentals',         3),
    ('CS407', 'Mobile App Development',             3),
    ('CS408', 'Computer Vision',                    3),
    ('CS409', 'Natural Language Processing',        3),
    ('CS410', 'DevOps & CI/CD',                     3),
    ('CS411', 'Blockchain Technology',              3),
    ('CS412', 'Internet of Things',                 3),
    ('CS413', 'Human Computer Interaction',         3),
]

ASSESSMENT_DATA = [
    ('Machine Learning Fundamentals Quiz',    'CS401', 'quiz',       30),
    ('Web Development Project',               'CS302', 'assignment', 50),
    ('Database Design Exam',                  'CS303', 'midterm',    40),
    ('Data Structures Assignment',            'CS304', 'assignment', 30),
    ('Software Engineering Case Study',       'CS305', 'assignment', 40),
    ('AI Ethics Essay',                       'CS402', 'assignment', 20),
    ('Big Data Analysis Report',              'CS301', 'assignment', 35),
    ('Network Security Quiz',                 'CS403', 'quiz',       25),
]

QUESTIONS_DATA = {
    'Machine Learning Fundamentals Quiz': [
        ('What is supervised learning?',
         'Supervised learning is a type of ML where the model is trained on labeled data to predict outputs for new inputs.',
         10),
        ('Explain overfitting and how to prevent it.',
         'Overfitting occurs when a model learns training data too well including noise. Prevention: regularization, cross-validation, more data.',
         10),
        ('What is a neural network?',
         'A neural network is a computational model inspired by the brain with interconnected layers of nodes that learn patterns.',
         10),
    ],
    'Web Development Project': [
        ('Explain the difference between GET and POST.',
         'GET retrieves data with parameters in URL. POST sends data in request body, used for forms and sensitive data.',
         15),
        ('What is Django MVT architecture?',
         'MVT: Model handles data, View contains business logic, Template handles HTML presentation.',
         15),
        ('Describe RESTful API principles.',
         'REST uses HTTP methods (GET, POST, PUT, DELETE), stateless communication, resource-based URLs, and standard status codes.',
         20),
    ],
    'Database Design Exam': [
        ('What is database normalization?',
         'Normalization organizes database to reduce redundancy. Forms: 1NF removes duplicates, 2NF removes partial dependencies, 3NF removes transitive dependencies.',
         15),
        ('Explain ACID properties.',
         'ACID: Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions), Durability (committed data persists).',
         15),
        ('What is an index in a database?',
         'An index is a data structure that improves query speed by creating a lookup table for column values, trading storage for performance.',
         10),
    ],
    'Data Structures Assignment': [
        ('Explain Big O notation.',
         'Big O notation describes algorithm time/space complexity in worst case. O(1) constant, O(n) linear, O(n²) quadratic.',
         10),
        ('What is a binary search tree?',
         'A BST is a tree where each node has at most two children, left child is smaller, right child is larger than parent.',
         10),
        ('Describe the difference between stack and queue.',
         'Stack is LIFO (Last In First Out). Queue is FIFO (First In First Out). Stack uses push/pop, Queue uses enqueue/dequeue.',
         10),
    ],
}

STUDENT_ANSWERS = [
    'Supervised learning uses labeled training data to learn a mapping from inputs to outputs for prediction.',
    'Overfitting is when the model memorizes training data. We can prevent it using dropout, regularization, and more training data.',
    'A neural network has input, hidden, and output layers with weighted connections that are adjusted during training.',
    'GET is used to retrieve data and parameters are in the URL. POST sends data in the body and is more secure.',
    'Django MVT separates concerns: Model for database, View for logic, Template for HTML display.',
    'REST APIs use standard HTTP methods, are stateless, and use resource-based URLs with JSON responses.',
    'Normalization reduces data redundancy by organizing tables into normal forms to eliminate anomalies.',
    'ACID ensures database transactions are reliable: atomic, consistent, isolated, and durable.',
    'An index speeds up database queries by creating a sorted reference to column values.',
    'Big O describes how algorithm performance scales with input size in the worst case scenario.',
    'A BST organizes data so left nodes are smaller and right nodes are larger enabling fast search.',
    'Stack is last in first out like a pile of plates. Queue is first in first out like a line of people.',
]

FEE_TYPES = [
    ('tuition',      450000, True),
    ('registration',  25000, True),
    ('library',       10000, False),
    ('ict',           15000, False),
]


class Command(BaseCommand):
    help = 'Simulate full university data: 26 students, 12 lecturers, 20 courses, submissions, grades, fees'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting simulation...')

        # Core setup
        faculty, _ = Faculty.objects.get_or_create(name='Faculty of Science & Technology')
        dept, _    = Department.objects.get_or_create(name='Computer Science', defaults={'faculty': faculty})
        semester, _= Semester.objects.get_or_create(name='Sem 2 2024/25', defaults={
            'start_date': '2025-01-15', 'end_date': '2025-06-30', 'is_current': True
        })

        # Create 12 lecturers
        lecturers = []
        for first, last, username in LECTURER_DATA:
            email = f'{username}@auca.ac.rw'
            u, created = CustomUser.objects.get_or_create(username=email, defaults={
                'email': email, 'first_name': first, 'last_name': last,
                'role': 'lecturer', 'is_active': True
            })
            if created:
                u.set_password('lecturer123')
                u.save()
            lecturers.append(u)
        self.stdout.write(f'  {len(lecturers)} lecturers ready')

        # Create 20 courses
        courses = []
        for i, (code, title, credits) in enumerate(COURSES_DATA):
            lecturer = lecturers[i % len(lecturers)]
            c, _ = Course.objects.get_or_create(code=code, defaults={
                'title': title, 'credits': credits,
                'department': dept, 'lecturer': lecturer
            })
            c.semester.add(semester)
            courses.append(c)
        self.stdout.write(f'  {len(courses)} courses ready')

        # Create 26 students
        students = []
        for i, (first, last, username) in enumerate(STUDENT_DATA):
            email = f'{username}@auca.ac.rw'
            u, created = CustomUser.objects.get_or_create(username=email, defaults={
                'email': email, 'first_name': first, 'last_name': last,
                'role': 'student', 'student_id': f'AUCA-2024-{1000+i:04d}',
                'is_active': True
            })
            if created:
                u.set_password('student123')
                u.save()
            students.append(u)
        self.stdout.write(f'  {len(students)} students ready')

        # Enroll each student in 5-8 random courses
        for student in students:
            num_courses = random.randint(5, 8)
            chosen = random.sample(courses, num_courses)
            for course in chosen:
                CourseEnrollment.objects.get_or_create(
                    student=student, course=course, semester=semester
                )

        # Add fees for each student
        for student in students:
            for fee_type, amount, is_paid in FEE_TYPES:
                Fee.objects.get_or_create(
                    student=student, fee_type=fee_type, semester=semester,
                    defaults={'amount': amount, 'is_paid': is_paid, 'due_date': '2025-06-30'}
                )

        # Create assessments with questions
        assessments = {}
        for title, course_code, atype, total in ASSESSMENT_DATA:
            course = Course.objects.filter(code=course_code).first()
            if not course or not course.lecturer:
                continue
            a, created = Assessment.objects.get_or_create(
                title=title, created_by=course.lecturer,
                defaults={
                    'description': f'Assessment for {course.title}',
                    'course': course, 'assessment_type': atype,
                    'total_marks': total,
                    'due_date': timezone.now() + timezone.timedelta(days=random.randint(3, 21))
                }
            )
            assessments[title] = a
            if created and title in QUESTIONS_DATA:
                for order, (qtext, model_ans, marks) in enumerate(QUESTIONS_DATA[title], 1):
                    Question.objects.create(
                        assessment=a, question_text=qtext,
                        model_answer=model_ans, marks=marks, order=order
                    )

        # Simulate student submissions with AI scoring
        submitted = 0
        graded = 0
        for student in students[:20]:  # first 20 students submit
            for title, assessment in assessments.items():
                questions = assessment.questions.all()
                if not questions:
                    continue
                # 70% chance student submits
                if random.random() < 0.7:
                    for question in questions:
                        answer_text = random.choice(STUDENT_ANSWERS)
                        ans, created = Answer.objects.get_or_create(
                            question=question, student=student,
                            defaults={'answer_text': answer_text}
                        )
                        if created:
                            # Simulate AI scoring
                            score = round(random.uniform(3.0, question.marks), 1)
                            similarity = round(random.uniform(0.45, 0.95), 4)
                            ans.ai_score = score
                            ans.similarity_score = similarity
                            ans.ai_feedback = _get_feedback(similarity)
                            # 60% chance lecturer already graded
                            if random.random() < 0.6:
                                ans.marks_obtained = round(score + random.uniform(-1, 1), 1)
                                ans.marks_obtained = max(0, min(ans.marks_obtained, question.marks))
                                ans.lecturer_feedback = random.choice([
                                    'Good understanding of the concept.',
                                    'Needs more detail in the explanation.',
                                    'Excellent answer, well structured.',
                                    'Partially correct, review the topic.',
                                    'Good effort, minor errors noted.',
                                ])
                                ans.status = 'graded'
                                ans.graded_by = assessment.created_by
                                graded += 1
                            ans.save()
                            submitted += 1

        self.stdout.write(f'  {submitted} answers submitted, {graded} graded')

        # Add grades for enrolled students
        grade_letters = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'D', 'F']
        grade_points  = [4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.0, 0.0]
        for student in students:
            enrollments = CourseEnrollment.objects.filter(student=student, semester=semester)
            for enrollment in enrollments:
                if not hasattr(enrollment, 'grade_record'):
                    idx = random.randint(0, len(grade_letters)-1)
                    Grade.objects.get_or_create(
                        enrollment=enrollment,
                        defaults={
                            'grade': grade_letters[idx],
                            'points': grade_points[idx],
                            'graded_by': enrollment.course.lecturer
                        }
                    )

        self.stdout.write(self.style.SUCCESS('\nSimulation complete!'))
        self.stdout.write('\n=== LOGIN CREDENTIALS ===')
        self.stdout.write('ADMIN:    admin@auca.ac.rw       / admin123')
        self.stdout.write('STUDENTS: <username>@auca.ac.rw  / student123')
        self.stdout.write('          e.g. jean.valentin@auca.ac.rw')
        self.stdout.write('LECTURERS:<username>@auca.ac.rw  / lecturer123')
        self.stdout.write('          e.g. prof.mutijima@auca.ac.rw')


def _get_feedback(similarity):
    if similarity >= 0.90: return 'Excellent answer! Closely matches the model answer.'
    elif similarity >= 0.75: return 'Good answer. Covers most key points.'
    elif similarity >= 0.60: return 'Satisfactory. Some key concepts present but incomplete.'
    elif similarity >= 0.45: return 'Partial answer. Several important points missing.'
    else: return 'Weak answer. Mostly off-topic or very incomplete.'
