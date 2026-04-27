from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser as User
from .decorators import student_required, lecturer_required, staff_required


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "accounts/login.html")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html")


def signup_view(request):
    if request.method == "POST":
        student_id       = request.POST.get("student_id", "").strip()
        first_name       = request.POST.get("first_name", "").strip()
        email            = request.POST.get("email", "").strip()
        password         = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        form_data = {"student_id": student_id, "first_name": first_name, "email": email}

        if not all([student_id, first_name, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        User.objects.create_user(username=email, email=email, password=password, first_name=first_name)
        messages.success(request, "Account created! Please log in.")
        return redirect("login")

    return render(request, "accounts/signup.html")


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, "accounts/forgot_password.html")
        messages.success(request, f"Reset instructions sent to {email}.")
    return render(request, "accounts/forgot_password.html")


@login_required(login_url='login')
def dashboard_view(request):
    from apps.courses.models import Course, Enrollment
    from apps.grades.models import Grade
    from apps.finances.models import FeeItem
    from apps.assessments.models import Assignment, Submission

    user = request.user

    # Courses
    if user.role == 'lecturer':
        courses = Course.objects.filter(lecturer=user)
    else:
        enrollments = Enrollment.objects.filter(student=user).select_related('course')
        courses = [e.course for e in enrollments]

    # Grades
    grades = Grade.objects.filter(student=user).select_related('course') if user.role == 'student' else []
    avg_score = round(sum(g.score for g in grades) / len(grades), 1) if grades else 0
    total_credits = sum(g.course.credits for g in grades)

    # Finances
    fees = FeeItem.objects.filter(student=user)
    balance_due = sum(f.amount for f in fees if f.status == 'due')

    # Assignments
    if user.role == 'lecturer':
        assignments = Assignment.objects.filter(lecturer=user).prefetch_related('questions')[:5]
        pending_submissions = Submission.objects.filter(question__assignment__lecturer=user, status='pending').count()
    else:
        assignments = Assignment.objects.all().prefetch_related('questions')[:5]
        pending_submissions = Submission.objects.filter(student=user, status='pending').count()

    context = {
        'user':                request.user,
        'email':               user.email,
        'role':                user.role.capitalize(),
        'courses':             courses,
        'grades':              grades,
        'avg_score':           avg_score,
        'total_credits':       total_credits,
        'fees':                fees,
        'balance_due':         balance_due,
        'assignments':         assignments,
        'pending_submissions': pending_submissions,
    }
    return render(request, 'accounts/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name  = request.POST.get('first_name', user.first_name)
        user.last_name   = request.POST.get('last_name', user.last_name)
        user.student_id  = request.POST.get('student_id', user.student_id)
        user.phone       = request.POST.get('phone', user.phone)
        user.bio         = request.POST.get('bio', user.bio)
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'user': request.user})


@student_required
def student_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Student Area'})


@lecturer_required
def lecturer_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Lecturer Area'})


@staff_required
def staff_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Staff Area'})
