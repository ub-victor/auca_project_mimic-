import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.accounts.decorators import lecturer_required, student_required
from .ai_evaluator import evaluate_answer, batch_evaluate
from .models import Assessment, Question, Answer

logger = logging.getLogger(__name__)

QuestionFormSet = inlineformset_factory(
    Assessment, Question,
    fields=['question_text', 'model_answer', 'marks', 'order'],
    extra=3, can_delete=True
)


@login_required(login_url='login')
def assignment_list(request):
    user = request.user
    if user.role in ('lecturer', 'staff'):
        # Lecturers see only their own assessments
        assessments = Assessment.objects.filter(created_by=user).prefetch_related('questions').order_by('-id')
    else:
        # Students see only assessments for courses they are enrolled in
        from apps.courses.models import CourseEnrollment
        from apps.core.models import Semester
        semester = Semester.objects.filter(is_current=True).first()
        enrolled_courses = CourseEnrollment.objects.filter(
            student=user, semester=semester
        ).values_list('course_id', flat=True) if semester else []
        assessments = Assessment.objects.filter(
            course_id__in=enrolled_courses
        ).prefetch_related('questions').order_by('-id')
    return render(request, 'assessments/assignment_list.html', {'assignments': assessments})


@lecturer_required
def assignment_create(request):
    from .forms import AssessmentForm
    from apps.courses.models import Course

    # Always limit course choices to lecturer's own courses
    lecturer_courses = Course.objects.filter(lecturer=request.user) if request.user.role == 'lecturer' else Course.objects.all()

    if request.method == 'POST':
        form    = AssessmentForm(request.POST)
        form.fields['course'].queryset = lecturer_courses
        formset = QuestionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            assessment            = form.save(commit=False)
            assessment.created_by = request.user
            assessment.save()
            formset.instance = assessment
            formset.save()
            messages.success(request, f'Assessment "{assessment.title}" created and visible to enrolled students.')
            return redirect('assessments:assignment_list')
        else:
            # Show form errors so lecturer knows what went wrong
            if form.errors:
                messages.error(request, f'Please fix the errors below: {form.errors}')
    else:
        form    = AssessmentForm()
        form.fields['course'].queryset = lecturer_courses
        formset = QuestionFormSet()

    return render(request, 'assessments/assignment_form.html', {'form': form, 'formset': formset})


@login_required(login_url='login')
def assignment_detail(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)
    questions  = assessment.questions.all()
    user       = request.user

    existing = {}
    if user.role == 'student':
        for ans in Answer.objects.filter(student=user, question__assessment=assessment):
            existing[ans.question_id] = ans

    if request.method == 'POST' and user.role == 'student':
        for question in questions:
            answer_text = request.POST.get(f'answer_{question.pk}', '').strip()
            answer_file = request.FILES.get(f'file_{question.pk}')
            if not answer_text and not answer_file:
                continue

            ans, _ = Answer.objects.get_or_create(question=question, student=user)

            if answer_file:
                try:
                    content = answer_file.read().decode('utf-8', errors='ignore').strip()
                    answer_text = content or answer_text
                    answer_file.seek(0)
                    ans.answer_file = answer_file
                except Exception:
                    pass

            ans.answer_text = answer_text

            if answer_text and question.model_answer:
                result = evaluate_answer(answer_text, question.model_answer, question.marks)
                ans.similarity_score = result['similarity_score']
                ans.ai_score         = result['ai_score']
                ans.ai_feedback      = result['ai_feedback']

            ans.save()

        messages.success(request, 'Answers submitted successfully!')
        return redirect('assessments:assignment_detail', pk=pk)

    return render(request, 'assessments/assignment_detail.html', {
        'assignment': assessment,
        'questions':  questions,
        'existing':   existing,
    })


@lecturer_required
def grade_submissions(request, assignment_pk):
    assessment = get_object_or_404(Assessment, pk=assignment_pk)
    # Only the creator or staff can grade
    if request.user.role not in ('staff',) and assessment.created_by != request.user:
        messages.error(request, 'You can only grade your own assessments.')
        return redirect('assessments:assignment_list')
    answers    = Answer.objects.filter(
        question__assessment=assessment
    ).select_related('student', 'question').order_by('question__order', 'student__username')

    if request.method == 'POST':
        ans_id   = request.POST.get('submission_id')
        score    = request.POST.get('final_score')
        feedback = request.POST.get('lecturer_feedback', '')
        ans      = get_object_or_404(Answer, pk=ans_id, question__assessment=assessment)
        ans.marks_obtained    = float(score) if score else ans.ai_score
        ans.lecturer_feedback = feedback
        ans.status            = 'graded'
        ans.graded_by         = request.user
        ans.save()
        messages.success(request, f'Grade saved for {ans.student.username}.')
        return redirect('assessments:grade_submissions', assignment_pk=assignment_pk)

    return render(request, 'assessments/grade_submissions.html', {
        'assignment':  assessment,
        'submissions': answers,
    })


@student_required
def my_results(request):
    answers = Answer.objects.filter(
        student=request.user
    ).select_related('question', 'question__assessment').order_by('-submitted_at')
    return render(request, 'assessments/my_results.html', {'submissions': answers})


@csrf_exempt
@require_POST
def evaluate_view(request):
    content_type = request.content_type or ""
    if "application/json" in content_type:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
        student_answer = data.get("student_answer", "").strip()
        model_answer   = data.get("model_answer", "").strip()
    else:
        student_answer = request.POST.get("student_answer", "").strip()
        model_answer   = request.POST.get("model_answer", "").strip()
        if "student_file" in request.FILES:
            student_answer = request.FILES["student_file"].read().decode("utf-8", errors="ignore").strip()
        if "model_file" in request.FILES:
            model_answer = request.FILES["model_file"].read().decode("utf-8", errors="ignore").strip()

    if not student_answer or not model_answer:
        return JsonResponse({"error": "Both answers are required."}, status=400)

    try:
        result = evaluate_answer(student_answer, model_answer)
        return JsonResponse(result)
    except Exception as exc:
        logger.exception("Evaluation failed: %s", exc)
        return JsonResponse({"error": str(exc)}, status=500)


@csrf_exempt
@require_POST
def batch_evaluate_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    pairs = data.get("pairs", [])
    if not isinstance(pairs, list) or not pairs:
        return JsonResponse({"error": "'pairs' must be a non-empty list."}, status=400)
    try:
        results = batch_evaluate([(s, m) for s, m in pairs])
        return JsonResponse({"results": results})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@login_required(login_url='login')
def evaluator_page(request):
    return render(request, 'assessments/evaluator.html')


@lecturer_required
def cheating_report(request, assessment_pk):
    """Run ML cheating detection for an assessment and notify lecturer."""
    from .ai_evaluator import detect_cheating_for_assessment
    from apps.accounts.models import Announcement

    assessment = get_object_or_404(Assessment, pk=assessment_pk)
    if request.user.role not in ('staff',) and assessment.created_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('assessments:assignment_list')

    suspects = detect_cheating_for_assessment(assessment_pk)

    # Auto-post notification to lecturer dashboard if suspects found
    if suspects and request.method == 'POST':
        names = ', '.join(set(
            f"{s['student_a'].get_full_name()} & {s['student_b'].get_full_name()}"
            for s in suspects[:3]
        ))
        Announcement.objects.create(
            title=f'Cheating Alert: {assessment.title}',
            body=f'ML detected {len(suspects)} suspected cheating case(s). Students: {names}. Please review.',
            audience='lecturers',
            created_by=request.user,
            is_active=True
        )
        messages.warning(request, f'Cheating alert posted to your dashboard. {len(suspects)} case(s) detected.')

    return render(request, 'assessments/cheating_report.html', {
        'assessment': assessment,
        'suspects':   suspects,
        'threshold':  0.92,
    })
