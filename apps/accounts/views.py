from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser as User
from .decorators import student_required, lecturer_required, staff_required
from django.contrib.auth.decorators import login_required


# Shared demo credentials
DEMO_USERS = {
    'student@auca.ac.rw':  {'password': 'student123',  'role': 'Student'},
    'staff@auca.ac.rw':    {'password': 'staff123',    'role': 'Staff'},
    'lecturer@auca.ac.rw': {'password': 'lecturer123', 'role': 'Lecturer'},
}

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
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html")


# ================= SIGNUP =================
def signup_view(request):
    if request.method == "POST":
        student_id       = request.POST.get("student_id", "").strip()
        first_name       = request.POST.get("first_name", "").strip()
        email            = request.POST.get("email", "").strip()
        password         = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        form_data = {
            "student_id": student_id,
            "first_name": first_name,
            "email": email,
        }

        # Validation
        if not all([student_id, first_name, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect("login")

    return render(request, "accounts/signup.html")


# ================= DASHBOARD =================
@login_required(login_url='login')
def dashboard_view(request):
    # Check if user is logged in
    if 'user_email' not in request.session:
        messages.error(request, "Please log in to access the dashboard.")
        return redirect("login")
    
    user_email = request.session['user_email']
    user_role = request.session['user_role']
    
    context = {
        'user_email': user_email,
        'user_role': user_role,
        'email': user_email,
        'role': user_role,
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
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'user': request.user})

# ================= STAFF ONLY =================
@student_required
def student_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Student Area'})

@lecturer_required
def lecturer_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Lecturer Area'})

@staff_required
def staff_area(request):
    return render(request, 'accounts/dashboard.html', {'role_label': 'Staff Area'})
