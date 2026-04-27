from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Course, CourseEnrollment
from apps.core.models import Semester
from apps.accounts.decorators import staff_required


@staff_required
def course_create(request):
    from apps.accounts.models import CustomUser
    from apps.core.models import Department
    if request.method == 'POST':
        code       = request.POST.get('code', '').strip()
        title      = request.POST.get('title', '').strip()
        credits    = request.POST.get('credits', 3)
        dept_id    = request.POST.get('department')
        lecturer_id= request.POST.get('lecturer')
        sem_id     = request.POST.get('semester')

        if not all([code, title, dept_id, sem_id]):
            messages.error(request, 'Please fill all required fields.')
        elif Course.objects.filter(code=code).exists():
            messages.error(request, f'Course code {code} already exists.')
        else:
            dept     = get_object_or_404(Department, pk=dept_id)
            lecturer = CustomUser.objects.filter(pk=lecturer_id).first() if lecturer_id else None
            semester = get_object_or_404(Semester, pk=sem_id)
            course   = Course.objects.create(code=code, title=title, credits=credits, department=dept, lecturer=lecturer)
            course.semester.add(semester)
            messages.success(request, f'Course "{title}" created successfully.')
            return redirect('dashboard')

    from apps.accounts.models import CustomUser
    from apps.core.models import Department
    return render(request, 'courses/course_form.html', {
        'departments': Department.objects.all(),
        'lecturers':   CustomUser.objects.filter(role='lecturer'),
        'semesters':   Semester.objects.all(),
    })


@staff_required
def course_edit(request, pk):
    from apps.accounts.models import CustomUser
    from apps.core.models import Department
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.title   = request.POST.get('title', course.title)
        course.credits = request.POST.get('credits', course.credits)
        lecturer_id    = request.POST.get('lecturer')
        course.lecturer= CustomUser.objects.filter(pk=lecturer_id).first() if lecturer_id else None
        course.save()
        messages.success(request, 'Course updated.')
        return redirect('dashboard')
    return render(request, 'courses/course_form.html', {
        'course':      course,
        'departments': Department.objects.all(),
        'lecturers':   CustomUser.objects.filter(role='lecturer'),
        'semesters':   Semester.objects.all(),
    })


@staff_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
    return redirect('dashboard')


@login_required(login_url='login')
def course_enroll(request, pk):
    if request.user.role != 'student':
        return HttpResponseForbidden()
    course   = get_object_or_404(Course, pk=pk)
    semester = Semester.objects.filter(is_current=True).first()
    if not semester:
        messages.error(request, 'No active semester found.')
        return redirect('dashboard')
    _, created = CourseEnrollment.objects.get_or_create(student=request.user, course=course, semester=semester)
    if created:
        messages.success(request, f'Enrolled in {course.title}.')
    else:
        messages.info(request, f'Already enrolled in {course.title}.')
    return redirect('dashboard')


@login_required(login_url='login')
def course_drop(request, pk):
    if request.user.role != 'student':
        return HttpResponseForbidden()
    course   = get_object_or_404(Course, pk=pk)
    semester = Semester.objects.filter(is_current=True).first()
    CourseEnrollment.objects.filter(student=request.user, course=course, semester=semester).delete()
    messages.success(request, f'Dropped {course.title}.')
    return redirect('dashboard')
