from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .models import CustomUser as User
from .forms import SignupForm, ProfileForm
from .decorators import student_required, lecturer_required, staff_required


# ================= HOME =================
def home_view(request):
    return render(request, 'home.html')


# ================= LOGIN =================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not email or not password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


# ================= SIGNUP =================
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect('login')


# ================= FORGOT PASSWORD =================
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'accounts/forgot_password.html')
        messages.success(request, f'Reset instructions sent to {email}. Please check your inbox.')
        return render(request, 'accounts/forgot_password.html', {'submitted_email': email})
    return render(request, 'accounts/forgot_password.html')


# ================= DASHBOARD =================
@login_required(login_url='/login/')
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})


# ================= PROFILE =================
@login_required(login_url='/login/')
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            # keep username in sync with email
            user.username = user.email
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})


# ================= ROLE-BASED AREAS =================
@student_required
def student_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Student Area'})


@lecturer_required
def lecturer_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Lecturer Area'})


@staff_required
def staff_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Staff Area'})
