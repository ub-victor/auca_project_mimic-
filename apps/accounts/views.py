from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import SignupForm, LoginForm, ProfileForm
from .decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        login_input = request.POST.get('email', '').strip()
        password    = request.POST.get('password', '').strip()

        if not login_input or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, 'accounts/login.html')

        from django.contrib.auth import get_user_model
        User = get_user_model()

        user_obj = None
        if '@' in login_input:
            user_obj = User.objects.filter(email=login_input).first()
        else:
            user_obj = User.objects.filter(student_id=login_input).first()

        user = authenticate(request, email=user_obj.email if user_obj else '', password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.email}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email/ID or password.")

    return render(request, 'accounts/login.html')


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, 'accounts/forgot_password.html')
        messages.success(request, f"Reset instructions sent to {email}. Check your terminal.")
    return render(request, 'accounts/forgot_password.html')


@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
