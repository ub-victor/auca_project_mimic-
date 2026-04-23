from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in.")
            return redirect('login')
        if request.user.role != 'student':
            messages.error(request, "Access restricted to students only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def lecturer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in.")
            return redirect('login')
        if request.user.role != 'lecturer':
            messages.error(request, "Access restricted to lecturers only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Allows staff, lecturers, and admins — manages both students and lecturers."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in.")
            return redirect('login')
        if request.user.role not in ('staff', 'lecturer') and not request.user.is_superuser:
            messages.error(request, "Access restricted to staff only.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
