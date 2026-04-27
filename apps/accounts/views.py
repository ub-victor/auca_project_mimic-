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
    context = {
        'user': request.user,
        'email': request.user.email,
        'role': request.user.get_role_display(),
        'user_role': request.user.get_role_display(),
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
