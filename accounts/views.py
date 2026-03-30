from django.shortcuts import render, redirect
from django.contrib import messages


# Shared demo credentials
DEMO_USERS = {
    'student@auca.ac.rw': {'password': 'student123', 'role': 'Student'},
    'staff@auca.ac.rw':   {'password': 'staff123',   'role': 'Staff'},
}

def login_view(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id", "").strip()
        password   = request.POST.get("password", "").strip()
        is_staff   = request.POST.get("is_staff", "0")

        if not student_id or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "accounts/login.html")

        # Placeholder: authentication logic goes here
        print("Login attempt — ID:", student_id, "| Staff:", bool(is_staff))
        return redirect("login")   # replace with redirect('dashboard') after auth

    return render(request, "accounts/login.html")


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, "accounts/forgot_password.html")

        # Placeholder: send reset email logic goes here
        print("Password reset requested for:", email)
        messages.success(request, f"Reset instructions sent to {email}. Please check your inbox.")
        return render(request, "accounts/forgot_password.html")

    return render(request, "accounts/forgot_password.html")


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

        if not all([student_id, first_name, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/signup.html", {"form_data": form_data})

        # Placeholder: save user to database here
        print("New account — ID:", student_id, "| Name:", first_name, "| Email:", email)
        messages.success(request, "Account created! Please log in.")
        return redirect("login")

    return render(request, "accounts/signup.html")
