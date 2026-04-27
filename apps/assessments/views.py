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
from .models import Assignment, Question, Submission

logger = logging.getLogger(__name__)

QuestionFormSet = inlineformset_factory(
    Assignment, Question,
    fields=['text', 'model_answer', 'max_score', 'order'],
    extra=3, can_delete=True
)


# ── Assignment list ───────────────────────────────────────────────────

@login_required(login_url='login')
def assignment_list(request):
    user = request.user
    if user.role in ('lecturer', 'staff'):
        assignments = Assignment.objects.filter(lecturer=user).prefetch_related('questions')
    else:
        assignments = Assignment.objects.all().prefetch_related('questions')
    return render(request, 'assessments/assignment_list.html', {'assignments': assignments})


# ── Create assignment (lecturer only) ────────────────────────────────

@lecturer_required
def assignment_create(request):
    from .forms import AssignmentForm
    if request.method == 'POST':
        form     = AssignmentForm(request.POST)
        formset  = QuestionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            assignment          = form.save(commit=False)
            assignment.lecturer = request.user
            assignment.save()
            formset.instance = assignment
            formset.save()
            messages.success(request, f'Assignment "{assignment.title}" created.')
            return redirect('assessments:assignment_list')
    else:
        form    = AssignmentForm()
        formset = QuestionFormSet()
    return render(request, 'assessments/assignment_form.html', {'form': form, 'formset': formset})


# ── Assignment detail + student submission ────────────────────────────

@login_required(login_url='login')
def assignment_detail(request, pk):
    assignment  = get_object_or_404(Assignment, pk=pk)
    questions   = assignment.questions.all()
    user        = request.user

    # Build existing submissions map for this student
    existing = {}
    if user.role == 'student':
        for sub in Submission.objects.filter(student=user, question__assignment=assignment):
            existing[sub.question_id] = sub

    if request.method == 'POST' and user.role == 'student':
        for question in questions:
            answer_text = request.POST.get(f'answer_{question.pk}', '').strip()
            answer_file = request.FILES.get(f'file_{question.pk}')

            if not answer_text and not answer_file:
                continue

            sub, _ = Submission.objects.get_or_create(question=question, student=user)

            if answer_file:
                sub.answer_file = answer_file
                # Extract text from file for AI evaluation
                try:
                    content = answer_file.read().decode('utf-8', errors='ignore').strip()
                    answer_text = content or answer_text
                    answer_file.seek(0)
                    sub.answer_file = answer_file
                except Exception:
                    pass

            sub.answer_text = answer_text

            # Run AI evaluation
            if answer_text:
                result = evaluate_answer(answer_text, question.model_answer, question.max_score)
                sub.similarity_score = result['similarity_score']
                sub.ai_score         = result['ai_score']
                sub.ai_feedback      = result['ai_feedback']

            sub.save()

        messages.success(request, 'Answers submitted successfully!')
        return redirect('assessments:assignment_detail', pk=pk)

    return render(request, 'assessments/assignment_detail.html', {
        'assignment': assignment,
        'questions':  questions,
        'existing':   existing,
    })


# ── Grading interface (lecturer) ──────────────────────────────────────

@lecturer_required
def grade_submissions(request, assignment_pk):
    assignment  = get_object_or_404(Assignment, pk=assignment_pk, lecturer=request.user)
    submissions = Submission.objects.filter(
        question__assignment=assignment
    ).select_related('student', 'question').order_by('question__order', 'student__username')

    if request.method == 'POST':
        sub_id       = request.POST.get('submission_id')
        final_score  = request.POST.get('final_score')
        feedback     = request.POST.get('lecturer_feedback', '')
        sub          = get_object_or_404(Submission, pk=sub_id, question__assignment=assignment)
        sub.final_score       = float(final_score) if final_score else sub.ai_score
        sub.lecturer_feedback = feedback
        sub.status            = 'graded'
        sub.graded_by         = request.user
        sub.save()
        messages.success(request, f'Grade saved for {sub.student.username}.')
        return redirect('assessments:grade_submissions', assignment_pk=assignment_pk)

    return render(request, 'assessments/grade_submissions.html', {
        'assignment':  assignment,
        'submissions': submissions,
    })


# ── Student results ───────────────────────────────────────────────────

@student_required
def my_results(request):
    submissions = Submission.objects.filter(
        student=request.user
    ).select_related('question', 'question__assignment').order_by('-submitted_at')
    return render(request, 'assessments/my_results.html', {'submissions': submissions})


# ── JSON API evaluate (used by evaluator page) ────────────────────────

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
