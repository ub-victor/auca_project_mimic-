"""
Full Simulation Command — AUCA Portal
Valentin NGANUCYE-SINGIZWA — Team 5

Simulates:
- All users with correct roles
- Course enrollments per semester
- Realistic student answers (varied quality)
- Cheating pairs (some students copy each other)
- AI evaluation on every answer
- Lecturer grading (approve or override AI)
- Fees per enrollment
- Grades per enrollment
- Analytics data visible in admin dashboard
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import CustomUser, Announcement
from apps.core.models import Faculty, Department, Semester
from apps.courses.models import Course, CourseEnrollment
from apps.assessments.models import Assessment, Question, Answer
from apps.finances.models import Fee
from apps.grades.models import Grade


# ── Realistic answer pools ────────────────────────────────────────────

GOOD_ANSWERS = [
    "Supervised learning is a machine learning approach where the model is trained on labeled data to learn a mapping from inputs to outputs for making predictions on new data.",
    "Supervised learning trains models using labeled examples where both input and expected output are provided, enabling the model to predict outcomes for unseen data.",
    "In supervised learning, the algorithm learns from a training dataset that contains input-output pairs, allowing it to generalize and make accurate predictions.",
    "Supervised learning uses labeled training data to build a predictive model. The algorithm learns the relationship between features and target labels.",
    "Supervised learning is when a model learns from labeled data, meaning each training example has a known answer, and the model learns to predict that answer.",
]

AVERAGE_ANSWERS = [
    "Supervised learning uses data with labels to train a model so it can predict things.",
    "It is a type of machine learning where you give the computer examples with answers and it learns from them.",
    "Supervised learning means the model is trained with labeled examples to make predictions.",
    "The model learns from labeled data and then predicts outputs for new inputs.",
    "Supervised learning trains on data that already has correct answers attached to it.",
]

WEAK_ANSWERS = [
    "Supervised learning is when computers learn by themselves.",
    "It is a machine learning method that uses data.",
    "The computer learns from examples.",
    "Supervised learning is a type of AI that predicts things.",
    "It uses algorithms to process information.",
]

# These are nearly identical — used to simulate cheating
CHEATING_ANSWER_A = "Supervised learning is a machine learning technique where the model is trained on labeled dataset containing input-output pairs to learn patterns and make predictions on new unseen data examples."
CHEATING_ANSWER_B = "Supervised learning is a machine learning technique where the model is trained on labeled dataset containing input-output pairs to learn patterns and make predictions on new unseen data."
CHEATING_ANSWER_C = "Supervised learning is a machine learning technique where model is trained on labeled dataset with input-output pairs to learn patterns and predict on new unseen data examples."

GOOD_ANSWERS_2 = [
    "Overfitting occurs when a model learns the training data too well including noise, resulting in poor performance on new data. Underfitting occurs when the model is too simple to capture the underlying patterns. Prevention: regularization, cross-validation, dropout, more training data.",
    "Overfitting means the model memorizes training data and fails to generalize. Underfitting means the model is too simple. We prevent overfitting using regularization, early stopping, and more data.",
    "Overfitting is when a model performs well on training data but poorly on test data because it learned noise. Underfitting is when the model cannot capture the pattern. Solutions include regularization and getting more data.",
]

GOOD_ANSWERS_3 = [
    "A neural network is a computational model inspired by the human brain consisting of layers of interconnected nodes called neurons. It has an input layer, hidden layers, and an output layer. Each connection has a weight that is adjusted during training through backpropagation.",
    "Neural networks are computing systems inspired by biological neural networks. They consist of input, hidden, and output layers with weighted connections. They learn by adjusting weights through backpropagation to minimize prediction error.",
    "A neural network is a deep learning model made of layers of artificial neurons. Information flows from input through hidden layers to output. Weights are updated during training using gradient descent and backpropagation.",
]

CHEATING_PAIRS = [
    # (student_a_username_fragment, student_b_username_fragment)
    ('jean.valentin', 'marie.uwase'),
    ('bosco.nshuti', 'deborah.mutijima'),
    ('hirwa.roy', 'clement.nzabonimpa'),
]


class Command(BaseCommand):
    help = 'Full simulation: answers, AI evaluation, cheating, grading, analytics'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting full simulation...'))

        # ── Get core objects ──────────────────────────────────────────
        semester = Semester.objects.filter(is_current=True).first()
        if not semester:
            self.stdout.write(self.style.ERROR('No current semester found. Run simulate first.'))
            return

        students  = list(CustomUser.objects.filter(role='student'))
        lecturers = list(CustomUser.objects.filter(role='lecturer'))
        courses   = list(Course.objects.all())
        assessments = list(Assessment.objects.prefetch_related('questions').all())

        self.stdout.write(f'  Found {len(students)} students, {len(lecturers)} lecturers, {len(courses)} courses, {len(assessments)} assessments')

        # ── Step 1: Ensure all students are enrolled in 4-7 courses ──
        self.stdout.write('  Step 1: Enrolling students in courses...')
        enrolled_count = 0
        for student in students:
            existing = set(CourseEnrollment.objects.filter(student=student, semester=semester).values_list('course_id', flat=True))
            available = [c for c in courses if c.id not in existing]
            needed = max(0, random.randint(4, 7) - len(existing))
            for course in random.sample(available, min(needed, len(available))):
                CourseEnrollment.objects.get_or_create(student=student, course=course, semester=semester)
                # Add fee per enrollment
                Fee.objects.get_or_create(
                    student=student, fee_type='tuition',
                    description=f'{course.code} — {course.title}',
                    semester=semester,
                    defaults={
                        'amount': Decimal(course.credits * 50000),
                        'is_paid': random.choice([True, True, False]),
                        'due_date': semester.end_date
                    }
                )
                enrolled_count += 1
        self.stdout.write(f'    {enrolled_count} new enrollments created')

        # ── Step 2: Submit answers for all assessments ────────────────
        self.stdout.write('  Step 2: Submitting student answers...')
        submitted = 0
        cheating_submitted = 0

        for assessment in assessments:
            questions = list(assessment.questions.all())
            if not questions:
                continue

            # Get enrolled students for this course
            enrolled_students = list(CustomUser.objects.filter(
                enrollments__course=assessment.course,
                enrollments__semester=semester,
                role='student'
            ).distinct())

            if not enrolled_students:
                enrolled_students = random.sample(students, min(15, len(students)))

            for student in enrolled_students:
                # 85% chance student submits
                if random.random() > 0.85:
                    continue

                for i, question in enumerate(questions):
                    # Choose answer quality based on student index (simulate grade distribution)
                    rand = random.random()
                    if rand < 0.25:
                        answer_text = random.choice(GOOD_ANSWERS if i == 0 else (GOOD_ANSWERS_2 if i == 1 else GOOD_ANSWERS_3))
                    elif rand < 0.55:
                        answer_text = random.choice(AVERAGE_ANSWERS)
                    else:
                        answer_text = random.choice(WEAK_ANSWERS)

                    ans, created = Answer.objects.get_or_create(
                        question=question, student=student,
                        defaults={'answer_text': answer_text}
                    )
                    if created:
                        submitted += 1

            # ── Inject cheating pairs ─────────────────────────────────
            for frag_a, frag_b in CHEATING_PAIRS:
                student_a = CustomUser.objects.filter(username__icontains=frag_a, role='student').first()
                student_b = CustomUser.objects.filter(username__icontains=frag_b, role='student').first()
                if not student_a or not student_b:
                    continue
                for i, question in enumerate(questions[:1]):  # first question only
                    cheat_texts = [CHEATING_ANSWER_A, CHEATING_ANSWER_B, CHEATING_ANSWER_C]
                    for student, cheat_text in [(student_a, cheat_texts[0]), (student_b, cheat_texts[1])]:
                        ans, created = Answer.objects.update_or_create(
                            question=question, student=student,
                            defaults={'answer_text': cheat_text}
                        )
                        if created:
                            cheating_submitted += 1

        self.stdout.write(f'    {submitted} answers submitted, {cheating_submitted} cheating answers injected')

        # ── Step 3: AI evaluate ALL answers ──────────────────────────
        self.stdout.write('  Step 3: Running AI evaluation on all answers...')
        from apps.assessments.ai_evaluator import evaluate_answer

        all_answers = Answer.objects.filter(ai_score__isnull=True).select_related('question')
        evaluated = 0
        for ans in all_answers:
            if not ans.answer_text or not ans.question.model_answer:
                continue
            try:
                result = evaluate_answer(ans.answer_text, ans.question.model_answer, ans.question.marks)
                ans.ai_score        = result['ai_score']
                ans.similarity_score= result['similarity_score']
                ans.ai_feedback     = result['ai_feedback']
                ans.save(update_fields=['ai_score', 'similarity_score', 'ai_feedback'])
                evaluated += 1
            except Exception as e:
                pass

        # Re-evaluate cheating answers to make sure similarity is high
        for frag_a, frag_b in CHEATING_PAIRS:
            for frag in [frag_a, frag_b]:
                student = CustomUser.objects.filter(username__icontains=frag).first()
                if not student:
                    continue
                for ans in Answer.objects.filter(student=student, ai_score__isnull=False):
                    # Force re-evaluate cheating answers
                    if ans.answer_text in [CHEATING_ANSWER_A, CHEATING_ANSWER_B, CHEATING_ANSWER_C]:
                        result = evaluate_answer(ans.answer_text, ans.question.model_answer, ans.question.marks)
                        ans.ai_score         = result['ai_score']
                        ans.similarity_score = result['similarity_score']
                        ans.ai_feedback      = result['ai_feedback']
                        ans.save(update_fields=['ai_score', 'similarity_score', 'ai_feedback'])

        self.stdout.write(f'    {evaluated} answers AI-evaluated')

        # ── Step 4: Lecturers grade submissions ───────────────────────
        self.stdout.write('  Step 4: Lecturers grading submissions...')
        graded = 0
        feedbacks = [
            'Good understanding of the concept.',
            'Excellent answer, well structured.',
            'Needs more detail in the explanation.',
            'Partially correct, review the topic.',
            'Good effort, minor errors noted.',
            'Very good, covers all key points.',
            'Acceptable but could be more precise.',
            'Outstanding response.',
        ]

        for assessment in assessments:
            lecturer = assessment.created_by
            answers  = Answer.objects.filter(
                question__assessment=assessment,
                ai_score__isnull=False,
                status='pending'
            ).select_related('student', 'question')

            for ans in answers:
                # 75% chance lecturer grades it
                if random.random() > 0.75:
                    continue
                # Lecturer approves AI score or slightly adjusts
                adjustment = random.choice([-0.5, 0, 0, 0, 0.5, 1.0])
                final = max(0, min(float(ans.ai_score) + adjustment, ans.question.marks))
                ans.marks_obtained    = Decimal(str(round(final, 1)))
                ans.lecturer_feedback = random.choice(feedbacks)
                ans.status            = 'graded'
                ans.graded_by         = lecturer
                ans.graded_at         = timezone.now() - timezone.timedelta(days=random.randint(0, 14))
                ans.save(update_fields=['marks_obtained', 'lecturer_feedback', 'status', 'graded_by', 'graded_at'])
                graded += 1

        self.stdout.write(f'    {graded} answers graded by lecturers')

        # ── Step 5: Add grades per enrollment ────────────────────────
        self.stdout.write('  Step 5: Assigning course grades...')
        grade_map = [
            ('A',  Decimal('4.0'), 90),
            ('A-', Decimal('3.7'), 85),
            ('B+', Decimal('3.3'), 80),
            ('B',  Decimal('3.0'), 75),
            ('B-', Decimal('2.7'), 70),
            ('C+', Decimal('2.3'), 65),
            ('C',  Decimal('2.0'), 60),
            ('D',  Decimal('1.0'), 50),
            ('F',  Decimal('0.0'), 30),
        ]
        grades_created = 0
        for enrollment in CourseEnrollment.objects.filter(semester=semester).select_related('student', 'course'):
            if not hasattr(enrollment, 'grade_record'):
                try:
                    # Weight toward B/C range for realistic distribution
                    weights = [5, 8, 12, 15, 12, 10, 8, 5, 3]
                    chosen = random.choices(grade_map, weights=weights, k=1)[0]
                    Grade.objects.get_or_create(
                        enrollment=enrollment,
                        defaults={
                            'grade':     chosen[0],
                            'points':    chosen[1],
                            'remarks':   random.choice(['Good performance', 'Satisfactory', 'Excellent', 'Needs improvement', 'Pass']),
                            'graded_by': enrollment.course.lecturer
                        }
                    )
                    grades_created += 1
                except Exception:
                    pass
        self.stdout.write(f'    {grades_created} course grades assigned')

        # ── Step 6: Post cheating alert announcements ─────────────────
        self.stdout.write('  Step 6: Posting cheating alerts...')
        admin = CustomUser.objects.filter(role='staff').first()
        if admin:
            for assessment in assessments[:3]:
                Announcement.objects.get_or_create(
                    title=f'Cheating Alert: {assessment.title}',
                    created_by=assessment.created_by,
                    defaults={
                        'body': f'ML cheating detection flagged suspicious submissions in "{assessment.title}". '
                                f'Please review the cheating report at /assessments/{assessment.pk}/cheating/ '
                                f'for details on suspected student pairs.',
                        'audience': 'lecturers',
                        'is_active': True,
                    }
                )
        self.stdout.write('    Cheating alert announcements posted')

        # ── Step 7: Mark some fees as paid ───────────────────────────
        self.stdout.write('  Step 7: Processing fee payments...')
        paid = Fee.objects.filter(is_paid=False).order_by('?')[:30]
        now  = timezone.now()
        for fee in paid:
            fee.is_paid = True
            fee.paid_at = now - timezone.timedelta(days=random.randint(1, 30))
            fee.save(update_fields=['is_paid', 'paid_at'])
        self.stdout.write(f'    {paid.count()} fees marked as paid')

        # ── Final summary ─────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(self.style.SUCCESS('SIMULATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(f'  Students:      {CustomUser.objects.filter(role="student").count()}')
        self.stdout.write(f'  Lecturers:     {CustomUser.objects.filter(role="lecturer").count()}')
        self.stdout.write(f'  Courses:       {Course.objects.count()}')
        self.stdout.write(f'  Assessments:   {Assessment.objects.count()}')
        self.stdout.write(f'  Total Answers: {Answer.objects.count()}')
        self.stdout.write(f'  AI Evaluated:  {Answer.objects.filter(ai_score__isnull=False).count()}')
        self.stdout.write(f'  Graded:        {Answer.objects.filter(status="graded").count()}')
        self.stdout.write(f'  Pending:       {Answer.objects.filter(status="pending").count()}')
        self.stdout.write(f'  Course Grades: {Grade.objects.count()}')
        self.stdout.write(f'  Fees:          {Fee.objects.count()} ({Fee.objects.filter(is_paid=True).count()} paid)')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('CHEATING PAIRS INJECTED (check /assessments/<id>/cheating/):'))
        self.stdout.write('  jean.valentin  <-> marie.uwase      (similarity ~0.97)')
        self.stdout.write('  bosco.nshuti   <-> deborah.mutijima (similarity ~0.96)')
        self.stdout.write('  hirwa.roy      <-> clement.nzabonimpa (similarity ~0.95)')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('LOGIN CREDENTIALS:'))
        self.stdout.write('  Admin:    admin@auca.ac.rw          / admin123')
        self.stdout.write('  Student:  jean.valentin@auca.ac.rw  / student123')
        self.stdout.write('  Lecturer: prof.mutijima@auca.ac.rw  / lecturer123')
