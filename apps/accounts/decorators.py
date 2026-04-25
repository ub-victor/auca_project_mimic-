from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy


def student_required(view_func):
    """Students only. Staff also passes."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('/login/')
        if request.user.role not in ('student', 'staff'):
            messages.error(request, "Access denied. Students only.")
            return redirect('/dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper


def lecturer_required(view_func):
    """
    Lecturers manage both students and lecturers.
    Allows: student, lecturer, staff.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('/login/')
        if request.user.role not in ('lecturer', 'student', 'staff'):
            messages.error(request, "Access denied.")
            return redirect('/dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Staff only — full access to everything."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to continue.")
            return redirect('/login/')
        if request.user.role != 'staff':
            messages.error(request, "Access denied. Staff only.")
            return redirect('/dashboard/')
        return view_func(request, *args, **kwargs)
    return wrapper
