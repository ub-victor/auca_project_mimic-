from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, models
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Course, CourseEnrollment, CourseSchedule
from apps.core.models import Semester, Department
from apps.accounts.models import CustomUser


@login_required
def course_list(request):
    """Display list of available courses with filtering and pagination"""
    courses = Course.objects.select_related('department', 'lecturer').prefetch_related('semester')

    # Filter by department if provided
    department_id = request.GET.get('department')
    if department_id:
        courses = courses.filter(department_id=department_id)

    # Filter by semester if provided
    semester_id = request.GET.get('semester')
    if semester_id:
        courses = courses.filter(semester_id=semester_id)

    # Search by course code or title
    search_query = request.GET.get('search')
    if search_query:
        courses = courses.filter(
            models.Q(code__icontains=search_query) |
            models.Q(title__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(courses, 12)  # 12 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'departments': Department.objects.all(),
        'semesters': Semester.objects.all(),
        'search_query': search_query,
        'selected_department': department_id,
        'selected_semester': semester_id,
    }
    return render(request, 'courses/course_list.html', context)


@login_required
def course_detail(request, course_id):
    """Display detailed information about a specific course"""
    course = get_object_or_404(
        Course.objects.select_related('department', 'lecturer').prefetch_related('semester', 'schedules'),
        id=course_id
    )

    # Get current semester (assuming there's a current semester)
    current_semester = Semester.objects.filter(is_current=True).first()

    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    if current_semester and request.user.role == 'student':
        enrollment = CourseEnrollment.objects.filter(
            student=request.user,
            course=course,
            semester=current_semester
        ).first()
        is_enrolled = enrollment is not None

    # Get schedules for current semester
    schedules = []
    if current_semester:
        schedules = course.schedules.filter(semester=current_semester).order_by('day_of_week', 'start_time')

    context = {
        'course': course,
        'schedules': schedules,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'current_semester': current_semester,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, course_id):
    """Handle course enrollment"""
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('course_detail', course_id=course_id)

    course = get_object_or_404(Course, id=course_id)
    current_semester = Semester.objects.filter(is_current=True).first()

    if not current_semester:
        messages.error(request, "No current semester is set.")
        return redirect('course_detail', course_id=course_id)

    # Check if already enrolled
    existing_enrollment = CourseEnrollment.objects.filter(
        student=request.user,
        course=course,
        semester=current_semester
    ).exists()

    if existing_enrollment:
        messages.warning(request, "You are already enrolled in this course.")
        return redirect('course_detail', course_id=course_id)

    try:
        CourseEnrollment.objects.create(
            student=request.user,
            course=course,
            semester=current_semester
        )
        messages.success(request, f"Successfully enrolled in {course.title}!")
    except IntegrityError:
        messages.error(request, "Enrollment failed. Please try again.")

    return redirect('course_detail', course_id=course_id)


@login_required
def unenroll_course(request, course_id):
    """Handle course unenrollment"""
    if request.user.role != 'student':
        messages.error(request, "Only students can unenroll from courses.")
        return redirect('course_detail', course_id=course_id)

    course = get_object_or_404(Course, id=course_id)
    current_semester = Semester.objects.filter(is_current=True).first()

    if not current_semester:
        messages.error(request, "No current semester is set.")
        return redirect('course_detail', course_id=course_id)

    enrollment = CourseEnrollment.objects.filter(
        student=request.user,
        course=course,
        semester=current_semester
    ).first()

    if not enrollment:
        messages.warning(request, "You are not enrolled in this course.")
        return redirect('course_detail', course_id=course_id)

    enrollment.delete()
    messages.success(request, f"Successfully unenrolled from {course.title}.")
    return redirect('course_detail', course_id=course_id)


@login_required
def timetable(request):
    """Display student's timetable grouped by day"""
    if request.user.role != 'student':
        messages.error(request, "Timetable is only available for students.")
        return redirect('dashboard')

    current_semester = Semester.objects.filter(is_current=True).first()
    if not current_semester:
        messages.error(request, "No current semester is set.")
        return render(request, 'courses/timetable.html', {'timetable': {}, 'current_semester': None})

    # Get enrolled courses with schedules
    enrollments = CourseEnrollment.objects.filter(
        student=request.user,
        semester=current_semester
    ).select_related('course')

    course_ids = [e.course_id for e in enrollments]
    schedules = CourseSchedule.objects.filter(
        course_id__in=course_ids,
        semester=current_semester
    ).select_related('course').order_by('day_of_week', 'start_time')

    # Group by day
    timetable = {}
    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in days_order:
        timetable[day] = []

    for schedule in schedules:
        timetable[schedule.day_of_week].append(schedule)

    context = {
        'timetable': timetable,
        'current_semester': current_semester,
        'days_order': days_order,
    }
    return render(request, 'courses/timetable.html', context)


@login_required
def lecturer_courses(request):
    """Lecturer course management"""
    if request.user.role != 'lecturer':
        messages.error(request, "Access denied. Lecturer privileges required.")
        return redirect('dashboard')

    # Get courses taught by this lecturer
    courses = Course.objects.filter(lecturer=request.user).select_related('department').prefetch_related('semester')

    # Get current semester
    current_semester = Semester.objects.filter(is_current=True).first()

    # Get enrollments for current semester
    enrollments = {}
    if current_semester:
        for course in courses:
            enrollments[course.id] = CourseEnrollment.objects.filter(
                course=course,
                semester=current_semester
            ).select_related('student').count()

    context = {
        'courses': courses,
        'enrollments': enrollments,
        'current_semester': current_semester,
    }
    return render(request, 'courses/lecturer_courses.html', context)


@login_required
def user_management(request):
    """Admin/Staff user management"""
    if request.user.role not in ['staff']:
        messages.error(request, "Access denied. Staff privileges required.")
        return redirect('dashboard')

    users = CustomUser.objects.all().order_by('username')

    # Filter by role if provided
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)

    # Search by username or email
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            models.Q(username__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'role_choices': CustomUser.ROLE_CHOICES,
        'search_query': search_query,
        'selected_role': role_filter,
    }
    return render(request, 'courses/user_management.html', context)
