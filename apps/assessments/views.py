import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .ai_evaluator import evaluate_answer
from .forms import AssessmentForm, QuestionFormSet, StudentAnswerForm, GradingForm
from .models import Assessment, Question, Submission, Answer

logger = logging.getLogger(__name__)


def _extract_text(uploaded_file) -> str:
    """Extract plain text from an uploaded .txt or .pdf file."""
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore").strip()
    if name.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(uploaded_file)
            return " ".join(page.extract_text() or "" for page in reader.pages).strip()
        except ImportError:
            raise ValueError("PDF support requires pypdf. Run: pip install pypdf")
    raise ValueError(f"Unsupported file type: {uploaded_file.name}. Use .txt or .pdf")


@login_required
def assessment_list(request):
    """List assessments for the current user."""
    user = request.user
    if user.role == 'lecturer':
        assessments = Assessment.objects.filter(created_by=user).select_related('course')
    elif user.role == 'student':
        assessments = Assessment.objects.filter(course__enrollments__student=user).select_related('course').distinct()
    else:
        assessments = Assessment.objects.all().select_related('course')

    return render(request, 'assessments/assessment_list.html', {'assessments': assessments})


@login_required
def assessment_detail(request, assessment_id):
    assessment = get_object_or_404(Assessment.objects.select_related('course', 'created_by').prefetch_related('questions'), id=assessment_id)
    submission = None
    student_answers = []

    if request.user.role == 'student':
        submission = Submission.objects.filter(assessment=assessment, student=request.user).first()
        if submission:
            student_answers = submission.answers.select_related('question').all()

    can_submit = request.user.role == 'student' and submission is None
    can_grade = request.user.role in ['lecturer', 'staff'] and (request.user == assessment.created_by or request.user.role == 'staff')

    return render(request, 'assessments/assessment_detail.html', {
        'assessment': assessment,
        'submission': submission,
        'student_answers': student_answers,
        'can_submit': can_submit,
        'can_grade': can_grade,
    })


@login_required
def create_assessment(request):
    if request.user.role not in ['lecturer', 'staff']:
        messages.error(request, 'Only lecturers and staff can create assessments.')
        return redirect('assessments:assessment_list')

    form = AssessmentForm(request.POST or None)
    formset = QuestionFormSet(request.POST or None)

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        assessment = form.save(commit=False)
        assessment.created_by = request.user
        assessment.save()
        formset.instance = assessment
        formset.save()
        messages.success(request, 'Assignment created successfully.')
        return redirect('assessments:assessment_detail', assessment_id=assessment.id)

    return render(request, 'assessments/assessment_create.html', {
        'form': form,
        'formset': formset,
    })


@login_required
def submit_assessment(request, assessment_id):
    if request.user.role != 'student':
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assessments:assessment_detail', assessment_id=assessment_id)

    assessment = get_object_or_404(Assessment.objects.prefetch_related('questions'), id=assessment_id)
    if Submission.objects.filter(assessment=assessment, student=request.user).exists():
        messages.warning(request, 'You have already submitted this assessment.')
        return redirect('assessments:assessment_detail', assessment_id=assessment.id)

    questions = list(assessment.questions.all())
    AnswerFormSet = formset_factory(StudentAnswerForm, extra=0)
    initial = [
        {
            'question_id': question.id,
            'question_text': question.question_text,
        }
        for question in questions
    ]

    if request.method == 'POST':
        formset = AnswerFormSet(request.POST, request.FILES, initial=initial)
        if formset.is_valid():
            submission = Submission.objects.create(assessment=assessment, student=request.user)
            question_map = {q.id: q for q in questions}
            total_similarity = 0.0
            total_score = 0.0
            evaluated_count = 0
            feedback_lines = []

            for form in formset:
                data = form.cleaned_data
                question = question_map.get(data['question_id'])
                answer_text = data.get('answer_text', '').strip()
                answer_file = data.get('answer_file')

                if answer_file and not answer_text:
                    answer_text = _extract_text(answer_file)

                answer = Answer.objects.create(
                    question=question,
                    submission=submission,
                    student=request.user,
                    answer_text=answer_text,
                    answer_file=answer_file,
                )

                if question.reference_answer:
                    result = evaluate_answer(answer_text, question.reference_answer)
                    total_similarity += result['similarity_score']
                    total_score += result['ai_score']
                    evaluated_count += 1
                    feedback_lines.append(
                        f"Q{question.order}: {result['ai_feedback']}"
                    )

            if evaluated_count:
                submission.similarity_score = round((total_similarity / evaluated_count) * 100, 2)
                submission.ai_score = round(total_score / evaluated_count, 2)
                submission.ai_feedback = '\n'.join(feedback_lines)
                submission.save()

            messages.success(request, 'Assignment submitted successfully. AI evaluation has been recorded.')
            return redirect('assessments:submission_detail', submission_id=submission.id)
    else:
        formset = AnswerFormSet(initial=initial)

    return render(request, 'assessments/submit_assessment.html', {
        'assessment': assessment,
        'questions': questions,
        'formset': formset,
    })


@login_required
def my_submissions(request):
    if request.user.role != 'student':
        messages.error(request, 'Only students can view their submissions.')
        return redirect('assessments:assessment_list')

    submissions = Submission.objects.filter(student=request.user).select_related('assessment__course')
    return render(request, 'assessments/my_submissions.html', {'submissions': submissions})


@login_required
def submission_list(request):
    if request.user.role not in ['lecturer', 'staff']:
        messages.error(request, 'Only lecturers and staff can view submissions.')
        return redirect('assessments:assessment_list')

    if request.user.role == 'lecturer':
        submissions = Submission.objects.filter(assessment__created_by=request.user).select_related('assessment', 'student')
    else:
        submissions = Submission.objects.all().select_related('assessment', 'student')

    return render(request, 'assessments/submission_list.html', {'submissions': submissions})


@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission.objects.select_related('assessment__course', 'student', 'assessment__created_by').prefetch_related('answers__question'), id=submission_id)

    if request.user.role == 'student' and submission.student != request.user:
        messages.error(request, 'Access denied.')
        return redirect('assessments:assessment_list')

    if request.user.role == 'lecturer' and submission.assessment.created_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('assessments:assessment_list')

    form = None
    if request.user.role in ['lecturer', 'staff']:
        form = GradingForm(request.POST or None, initial={
            'final_grade': submission.final_grade,
            'lecturer_feedback': submission.lecturer_feedback,
            'status': submission.status,
        })
        if request.method == 'POST' and form.is_valid():
            submission.final_grade = form.cleaned_data['final_grade']
            submission.lecturer_feedback = form.cleaned_data['lecturer_feedback']
            submission.status = form.cleaned_data['status']
            if submission.status == 'graded' and submission.graded_at is None:
                submission.graded_at = timezone.now()
            submission.save()
            messages.success(request, 'Submission evaluated and updated successfully.')
            return redirect('assessments:submission_detail', submission_id=submission.id)

    return render(request, 'assessments/submission_detail.html', {
        'submission': submission,
        'form': form,
    })


@csrf_exempt
@require_POST
def evaluate_view(request):
    content_type = request.content_type or ""

    if "application/json" in content_type:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body."}, status=400)
        student_answer = data.get("student_answer", "").strip()
        model_answer = data.get("model_answer", "").strip()
    else:
        student_answer = request.POST.get("student_answer", "").strip()
        model_answer = request.POST.get("model_answer", "").strip()
        if "student_file" in request.FILES:
            try:
                student_answer = _extract_text(request.FILES["student_file"])
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)
        if "model_file" in request.FILES:
            try:
                model_answer = _extract_text(request.FILES["model_file"])
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)

    if not student_answer or not model_answer:
        return JsonResponse({"error": "Both student_answer and model_answer are required (text or file)."}, status=400)

    try:
        result = evaluate_answer(student_answer, model_answer)
        logger.info("Evaluation complete — ai_score=%.2f", result["ai_score"])
        return JsonResponse(result)
    except Exception as exc:
        logger.exception("Evaluation failed: %s", exc)
        return JsonResponse({"error": "Evaluation failed.", "detail": str(exc)}, status=500)


@csrf_exempt
@require_POST
def batch_evaluate_view(request):
    from .ai_evaluator import batch_evaluate

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    pairs = data.get("pairs", [])
    if not isinstance(pairs, list) or not pairs:
        return JsonResponse({"error": "'pairs' must be a non-empty list."}, status=400)

    try:
        results = batch_evaluate([(s, m) for s, m in pairs])
        return JsonResponse({"results": results})
    except Exception as exc:
        logger.exception("Batch evaluation failed: %s", exc)
        return JsonResponse({"error": "Batch evaluation failed.", "detail": str(exc)}, status=500)
