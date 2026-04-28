import io
import base64
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.accounts.decorators import staff_required, student_required
from apps.accounts.models import CustomUser
from apps.assessments.models import Answer, Assessment
from apps.courses.models import CourseEnrollment, Course
from apps.grades.models import Grade


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_b64


@staff_required
def analytics_dashboard(request):
    charts = {}

    # 1. Grade distribution across all students
    grades = Grade.objects.all()
    grade_counts = {}
    for g in grades:
        grade_counts[g.grade] = grade_counts.get(g.grade, 0) + 1

    if grade_counts:
        fig, ax = plt.subplots(figsize=(8, 4))
        labels = sorted(grade_counts.keys())
        values = [grade_counts[l] for l in labels]
        colors = ['#2e7d32' if l in ('A','A-') else '#1565c0' if l in ('B+','B','B-')
                  else '#e67e22' if l in ('C+','C') else '#c0392b' for l in labels]
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=0.5)
        ax.set_title('Grade Distribution — All Students', fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel('Grade', fontsize=10)
        ax.set_ylabel('Number of Students', fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, str(val),
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        fig.patch.set_facecolor('#f8f9fa')
        charts['grade_dist'] = _fig_to_base64(fig)

    # 2. AI Score vs Lecturer Score scatter plot
    answers = Answer.objects.filter(ai_score__isnull=False, marks_obtained__isnull=False)
    if answers.count() > 0:
        ai_scores  = [float(a.ai_score) for a in answers]
        lec_scores = [float(a.marks_obtained) for a in answers]
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(ai_scores, lec_scores, alpha=0.6, color='#2a9d8f', edgecolors='white', s=60)
        max_val = max(max(ai_scores), max(lec_scores)) + 1
        ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='Perfect agreement')
        ax.set_title('AI Score vs Lecturer Score', fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel('AI Score', fontsize=10)
        ax.set_ylabel('Lecturer Score', fontsize=10)
        ax.legend(fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.patch.set_facecolor('#f8f9fa')
        charts['ai_vs_lec'] = _fig_to_base64(fig)

    # 3. ML Prediction: Students at risk of failing
    students = CustomUser.objects.filter(role='student')
    at_risk_names, at_risk_gpas = [], []
    safe_names, safe_gpas = [], []
    for student in students:
        student_grades = Grade.objects.filter(enrollment__student=student)
        if student_grades.exists():
            avg_gpa = sum(float(g.points) for g in student_grades) / student_grades.count()
            name = f"{student.first_name} {student.last_name[0]+'.' if student.last_name else ''}"
            if avg_gpa < 2.0:
                at_risk_names.append(name)
                at_risk_gpas.append(avg_gpa)
            elif avg_gpa < 2.7:
                safe_names.append(name)
                safe_gpas.append(avg_gpa)

    if at_risk_names or safe_names:
        fig, ax = plt.subplots(figsize=(10, 5))
        x_risk = range(len(at_risk_names))
        x_safe = range(len(at_risk_names), len(at_risk_names) + len(safe_names))
        ax.bar(x_risk, at_risk_gpas, color='#c0392b', label='At Risk (GPA < 2.0)', alpha=0.85)
        ax.bar(x_safe, safe_gpas, color='#e67e22', label='Warning (GPA < 2.7)', alpha=0.85)
        ax.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='Fail threshold (2.0)')
        ax.axhline(y=2.7, color='orange', linestyle='--', alpha=0.7, label='Warning threshold (2.7)')
        all_names = at_risk_names + safe_names
        all_x = list(x_risk) + list(x_safe)
        ax.set_xticks(all_x)
        ax.set_xticklabels(all_names, rotation=45, ha='right', fontsize=8)
        ax.set_title('ML Prediction: Students at Risk of Failing', fontsize=13, fontweight='bold', pad=12)
        ax.set_ylabel('GPA', fontsize=10)
        ax.set_ylim(0, 4.5)
        ax.legend(fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.patch.set_facecolor('#f8f9fa')
        charts['at_risk'] = _fig_to_base64(fig)

    # 4. Submissions per assessment
    assessments = Assessment.objects.all()
    if assessments.exists():
        a_titles = [a.title[:20] + '...' if len(a.title) > 20 else a.title for a in assessments]
        a_counts = [Answer.objects.filter(question__assessment=a).values('student').distinct().count() for a in assessments]
        fig, ax = plt.subplots(figsize=(10, 4))
        bars = ax.barh(a_titles, a_counts, color='#2d4d68', alpha=0.85)
        ax.set_title('Student Submissions per Assessment', fontsize=13, fontweight='bold', pad=12)
        ax.set_xlabel('Number of Students Submitted', fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for bar, val in zip(bars, a_counts):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    str(val), va='center', fontsize=9)
        fig.patch.set_facecolor('#f8f9fa')
        charts['submissions'] = _fig_to_base64(fig)

    # Stats
    total_students  = CustomUser.objects.filter(role='student').count()
    total_lecturers = CustomUser.objects.filter(role='lecturer').count()
    total_answers   = Answer.objects.count()
    ai_graded       = Answer.objects.filter(ai_score__isnull=False).count()
    at_risk_count   = len(at_risk_names)

    return render(request, 'core/analytics.html', {
        'charts': charts,
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'total_answers': total_answers,
        'ai_graded': ai_graded,
        'at_risk_count': at_risk_count,
    })


@login_required(login_url='login')
def timetable_download(request):
    """Generate a simple text timetable for the logged-in student."""
    from apps.core.models import Semester
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = ['08:00-10:00', '10:00-12:00', '14:00-16:00', '16:00-18:00']

    semester = Semester.objects.filter(is_current=True).first()
    if request.user.role == 'student':
        enrollments = CourseEnrollment.objects.filter(
            student=request.user, semester=semester
        ).select_related('course') if semester else []
        courses = [e.course for e in enrollments]
    else:
        courses = Course.objects.filter(lecturer=request.user)

    lines = [
        f"AUCA PORTAL — TIMETABLE",
        f"Student: {request.user.get_full_name()}",
        f"Email:   {request.user.email}",
        f"Semester: {semester.name if semester else 'N/A'}",
        "=" * 50,
        ""
    ]
    for i, course in enumerate(courses):
        day  = days[i % len(days)]
        time = times[i % len(times)]
        lines.append(f"{day:<12} {time}  {course.code}  {course.title}")
    lines += ["", "=" * 50, "Generated by AUCA Portal"]

    content = "\n".join(lines)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="timetable.txt"'
    return response
