import json
import logging

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .ai_evaluator import evaluate_answer

logger = logging.getLogger(__name__)

ALLOWED_ROLES = {"Staff", "Lecturer"}


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


def evaluator_page(request):
    """Renders the evaluator UI — Staff/Lecturer only."""
    role = request.session.get("user_role", "")
    if role not in ALLOWED_ROLES:
        return redirect("login")
    return render(request, "assessments/evaluator.html", {"user_role": role})


@csrf_exempt
@require_POST
def evaluate_view(request):
    """
    POST /assessments/evaluate/
    Accepts JSON body OR multipart form with optional file uploads.
    """
    # --- parse input (JSON or multipart) ---
    content_type = request.content_type or ""

    if "application/json" in content_type:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body."}, status=400)
        student_answer = data.get("student_answer", "").strip()
        model_answer   = data.get("model_answer", "").strip()
    else:
        # multipart/form-data — text fields + optional file uploads
        student_answer = request.POST.get("student_answer", "").strip()
        model_answer   = request.POST.get("model_answer", "").strip()

        # File overrides text if provided
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
        return JsonResponse(
            {"error": "Both student_answer and model_answer are required (text or file)."},
            status=400,
        )

    try:
        result = evaluate_answer(student_answer, model_answer)
        logger.info("Evaluation complete — final_score=%.2f", result["final_score"])
        return JsonResponse(result)
    except Exception as exc:
        logger.exception("Evaluation failed: %s", exc)
        return JsonResponse({"error": "Evaluation failed.", "detail": str(exc)}, status=500)


@csrf_exempt
@require_POST
def batch_evaluate_view(request):
    """POST /assessments/evaluate/batch/"""
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
