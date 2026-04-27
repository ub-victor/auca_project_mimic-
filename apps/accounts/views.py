from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser as User
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

    user = request.user

    # Courses
    if user.role == 'lecturer':
        courses = Course.objects.filter(lecturer=user)
    else:
        enrollments = CourseEnrollment.objects.filter(student=user).select_related('course')
        courses = [e.course for e in enrollments]

    # Assessments
    if user.role in ('lecturer', 'staff'):
        assessments = Assessment.objects.filter(created_by=user)[:5]
        pending_count = Answer.objects.filter(question__assessment__created_by=user, status='pending').count()
    else:
        assessments = Assessment.objects.all()[:5]
        pending_count = Answer.objects.filter(student=user, status='pending').count()

    context = {
        'user':          user,
        'email':         user.email,
        'role':          user.get_role_display(),
        'user_role':     user.get_role_display(),
        'courses':       courses,
        'assessments':   assessments,
        'pending_count': pending_count,
    }
    return render(request, "accounts/dashboard.html", context)


def logout_view(request):
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
