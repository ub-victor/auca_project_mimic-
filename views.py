from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, ProfileForm        # ← import forms
from .decorators import student_required, lecturer_required, staff_required

# ================= LOGIN =================
def login_view(request):
    if request.method == 'POST':
        email    = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'student':
                return redirect('student_area')
            elif user.role == 'lecturer':
                return redirect('lecturer_area')
            else:
                return redirect('staff_area')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')


# ================= SIGNUP — now uses SignupForm =================
def signup_view(request):
    form = SignupForm(request.POST or None)      # ← use form, not raw POST
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
        # form.errors will show automatically in template

    return render(request, 'accounts/signup.html', {'form': form})


# ================= DASHBOARD — now protected by decorator =================
@login_required(login_url='login')             # ← decorator instead of manual check
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out.')
    return redirect('login')


# ================= PROFILE — uses ProfileForm =================
@login_required(login_url='login')
def profile_view(request):
    form = ProfileForm(request.POST or None,
                       request.FILES or None,
                       instance=request.user)  # ← form pre-filled with current user
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {'form': form})


# ================= ROLE AREAS =================
@student_required
def student_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Student Area'})

@lecturer_required
def lecturer_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Lecturer Area'})

@staff_required
def staff_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Staff Area'})
