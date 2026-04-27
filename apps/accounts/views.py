from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser as User, AuditLog
from .decorators import student_required, lecturer_required, staff_required
from .forms import LoginForm, SignupForm, ProfileForm


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email    = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user     = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            AuditLog.objects.create(user=user, action='login', target='dashboard',
                detail='Login successful', ip_address=request.META.get('REMOTE_ADDR'))
            return redirect("dashboard")
        messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html", {'form': form})


def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")
    return render(request, "accounts/signup.html", {'form': form})


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            messages.error(request, "Please enter your email address.")
        else:
            messages.success(request, f"Reset instructions sent to {email}.")
    return render(request, "accounts/forgot_password.html")


@login_required(login_url='login')
def dashboard_view(request):
    from apps.courses.models import Course, CourseEnrollment
    from apps.assessments.models import Assessment, Answer
    from apps.accounts.models import CustomUser
    from apps.finances.models import Fee
    from apps.core.models import Semester

    user = request.user
    context = {'user': user, 'email': user.email, 'role': user.get_role_display()}

    if user.role == 'student':
        semester = Semester.objects.filter(is_current=True).first()
        enrollments = CourseEnrollment.objects.filter(student=user).select_related('course') if semester else []
        enrolled_courses = [e.course for e in enrollments]
        enrolled_ids = [c.id for c in enrolled_courses]
        available_courses = Course.objects.exclude(id__in=enrolled_ids)
        fees = Fee.objects.filter(student=user)
        balance_due = sum(f.amount for f in fees if not f.is_paid)
        assessments = Assessment.objects.all().prefetch_related('questions')[:5]
        pending_answers = Answer.objects.filter(student=user, status='pending').count()
        graded_answers = Answer.objects.filter(student=user, status='graded')
        graded_count = graded_answers.count()
        avg_score = round(sum(float(a.marks_obtained or 0) for a in graded_answers) / graded_count, 1) if graded_count else 0
        context.update({
            'enrolled_courses': enrolled_courses,
            'available_courses': available_courses,
            'fees': fees, 'balance_due': balance_due,
            'assessments': assessments,
            'pending_answers': pending_answers,
            'graded_count': graded_count,
            'avg_score': avg_score,
            'total_credits': sum(c.credits for c in enrolled_courses),
        })

    elif user.role == 'lecturer':
        my_courses = Course.objects.filter(lecturer=user).prefetch_related('enrollments')
        my_assessments = Assessment.objects.filter(created_by=user).prefetch_related('questions')
        pending_submissions = Answer.objects.filter(
            question__assessment__created_by=user, status='pending'
        ).select_related('student', 'question__assessment')
        total_students = sum(c.enrollments.count() for c in my_courses)
        context.update({
            'my_courses': my_courses,
            'my_assessments': my_assessments,
            'pending_submissions': pending_submissions,
            'total_students': total_students,
            'pending_count': pending_submissions.count(),
        })

    elif user.role == 'staff':
        all_courses = Course.objects.all().select_related('lecturer', 'department')
        total_students = CustomUser.objects.filter(role='student').count()
        total_lecturers = CustomUser.objects.filter(role='lecturer').count()
        all_fees = Fee.objects.filter(is_paid=False)
        unpaid_total = sum(f.amount for f in all_fees)
        all_assessments = Assessment.objects.all()
        total_answers = Answer.objects.count()
        ai_graded = Answer.objects.filter(ai_score__isnull=False).count()
        overridden = Answer.objects.filter(marks_obtained__isnull=False, status='graded').count()
        context.update({
            'all_courses': all_courses,
            'total_students': total_students,
            'total_lecturers': total_lecturers,
            'unpaid_total': unpaid_total,
            'unpaid_count': all_fees.count(),
            'total_answers': total_answers,
            'ai_graded': ai_graded,
            'overridden': overridden,
            'all_lecturers': CustomUser.objects.filter(role='lecturer'),
            'all_users': CustomUser.objects.all().order_by('role'),
        })

    if user.role == 'student':
        return render(request, 'accounts/dashboard_student.html', context)
    elif user.role == 'lecturer':
        return render(request, 'accounts/dashboard_lecturer.html', context)
    else:
        return render(request, 'accounts/dashboard_admin.html', context)


def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(user=request.user, action='logout', target='login',
            detail='User logged out', ip_address=request.META.get('REMOTE_ADDR'))
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


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


@student_required
def student_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Student Area'})


@lecturer_required
def lecturer_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Lecturer Area'})


@staff_required
def staff_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Staff Area'})
