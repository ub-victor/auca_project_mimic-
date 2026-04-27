from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import CustomUser as User
from .decorators import student_required, lecturer_required, staff_required
from .forms import LoginForm, SignupForm, ProfileForm
from apps.courses.models import CourseEnrollment
from apps.finances.models import Fee
from apps.grades.models import Grade


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html", {'form': form})


# ================= SIGNUP =================
def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "accounts/signup.html", {'form': form})


# ================= DASHBOARD =================
@login_required(login_url='login')
def dashboard_view(request):
    enrollments = CourseEnrollment.objects.filter(student=request.user).select_related('course', 'semester')
    fee_records = Fee.objects.filter(student=request.user).select_related('semester').order_by('semester__start_date', 'due_date')
    grades = Grade.objects.filter(enrollment__student=request.user).select_related('enrollment__course')

    latest_semester = enrollments.order_by('-semester__start_date').first()
    semester_name = latest_semester.semester.name if latest_semester else 'Current semester'
    academic_year = latest_semester.semester.name if latest_semester else 'Academic Year'

    timetable_slots = [
        ('MON', '08:00 – 10:00'),
        ('TUE', '10:00 – 12:00'),
        ('WED', '08:00 – 10:00'),
        ('THU', '14:00 – 16:00'),
        ('FRI', '10:00 – 12:00'),
    ]

    timetable = []
    for index, enrollment in enumerate(enrollments[:5]):
        day, time = timetable_slots[index % len(timetable_slots)]
        timetable.append({
            'day': day,
            'time': time,
            'course': enrollment.course.title,
            'credits': enrollment.course.credits,
        })

    enrolled_courses = [
        {
            'code': enrollment.course.code,
            'title': enrollment.course.title,
            'credits': enrollment.course.credits,
        }
        for enrollment in enrollments
    ]

    grade_points = [float(grade.points) for grade in grades]
    gpa = round(sum(grade_points) / len(grade_points), 2) if grade_points else None
    average_score = f"{round((gpa / 4) * 100, 0)}%" if gpa is not None else 'N/A'

    fee_items = [
        {
            'label': fee.get_fee_type_display(),
            'amount': f"RWF {fee.amount:,.0f}",
            'is_paid': fee.is_paid,
            'status': 'Paid' if fee.is_paid else 'Due',
        }
        for fee in fee_records
    ]
    balance_due = f"RWF {sum(fee.amount for fee in fee_records if not fee.is_paid):,.0f}"
    due_tasks = fee_records.filter(is_paid=False).count()

    announcements = [
        {'title': 'End-of-semester exams schedule released', 'date': 'June 10, 2025'},
        {'title': 'Library hours extended through exam period', 'date': 'June 8, 2025'},
        {'title': 'Registration open for Semester 3 courses', 'date': 'June 5, 2025'},
        {'title': 'Campus Wi-Fi maintenance scheduled Saturday', 'date': 'June 3, 2025'},
    ]

    context = {
        'user': request.user,
        'email': request.user.email,
        'role': request.user.get_role_display(),
        'user_role': request.user.get_role_display(),
        'semester_name': semester_name,
        'academic_year': academic_year,
        'enrollments_count': enrollments.count(),
        'courses_count': enrollments.count(),
        'credits_total': sum(enrollment.course.credits for enrollment in enrollments),
        'timetable': timetable,
        'enrolled_courses': enrolled_courses,
        'gpa': gpa,
        'average_score': average_score,
        'fee_items': fee_items,
        'balance_due': balance_due,
        'due_tasks': due_tasks,
        'announcements': announcements,
    }
    return render(request, "accounts/dashboard.html", context)


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# ================= PROFILE =================
@login_required(login_url='login')
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.username = profile.email
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})


# ================= ROLE-RESTRICTED AREAS =================
@student_required
def student_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Student Area'})


@lecturer_required
def lecturer_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Lecturer Area'})


@staff_required
def staff_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Staff Area'})
