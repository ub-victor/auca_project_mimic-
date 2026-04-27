from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from decouple import config
from .models import CustomUser as User, AuditLog
from .decorators import student_required, lecturer_required, staff_required
from .forms import LoginForm, SignupForm


def _log(request, action, target='', detail=''):
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        AuditLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action=action, target=target, detail=detail, ip_address=ip or None
        )
    except Exception:
        pass


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email    = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user     = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            _log(request, 'login', 'dashboard', 'Login successful')
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
    from apps.finances.models import Fee
    from apps.core.models import Semester
    from .models import Announcement

    user = request.user
    context = {'user': user, 'email': user.email, 'role': user.get_role_display()}

    if user.role == 'student':
        semester = Semester.objects.filter(is_current=True).first()
        enrollments = CourseEnrollment.objects.filter(student=user).select_related('course') if semester else []
        enrolled_courses = [e.course for e in enrollments]
        enrolled_ids = [c.id for c in enrolled_courses]
        available_courses = Course.objects.exclude(id__in=enrolled_ids)
        fees = Fee.objects.filter(student=user)
        balance_due = sum(f.amount for f in fees if not f.is_paid)
        assessments = Assessment.objects.all().prefetch_related('questions')[:5]
        pending_answers = Answer.objects.filter(student=user, status='pending').count()
        graded_answers = Answer.objects.filter(student=user, status='graded')
        graded_count = graded_answers.count()
        avg_score = round(sum(float(a.marks_obtained or 0) for a in graded_answers) / graded_count, 1) if graded_count else 0
        notifications = Announcement.objects.filter(
            is_active=True
        ).filter(Q(audience='all') | Q(audience='students') | Q(course__in=enrolled_courses)).distinct().order_by('-created_at')[:5]
        context.update({
            'enrolled_courses': enrolled_courses,
            'available_courses': available_courses,
            'fees': fees, 'balance_due': balance_due,
            'assessments': assessments,
            'pending_answers': pending_answers,
            'graded_count': graded_count,
            'avg_score': avg_score,
            'total_credits': sum(c.credits for c in enrolled_courses),
            'notifications': notifications,
        })

    elif user.role == 'lecturer':
        my_courses = Course.objects.filter(lecturer=user).prefetch_related('enrollments')
        my_assessments = Assessment.objects.filter(created_by=user).prefetch_related('questions')
        pending_submissions = Answer.objects.filter(
            question__assessment__created_by=user, status='pending'
        ).select_related('student', 'question__assessment')
        total_students = sum(c.enrollments.count() for c in my_courses)
        notifications = Announcement.objects.filter(
            is_active=True
        ).filter(Q(audience='all') | Q(audience='lecturers') | Q(created_by=user)).distinct().order_by('-created_at')[:5]
        context.update({
            'my_courses': my_courses,
            'my_assessments': my_assessments,
            'pending_submissions': pending_submissions,
            'total_students': total_students,
            'pending_count': pending_submissions.count(),
            'notifications': notifications,
        })

    elif user.role == 'staff':
        all_courses = Course.objects.all().select_related('lecturer', 'department')
        total_students = User.objects.filter(role='student').count()
        total_lecturers = User.objects.filter(role='lecturer').count()
        all_fees = Fee.objects.filter(is_paid=False)
        unpaid_total = sum(f.amount for f in all_fees)
        total_answers = Answer.objects.count()
        ai_graded = Answer.objects.filter(ai_score__isnull=False).count()
        overridden = Answer.objects.filter(marks_obtained__isnull=False, status='graded').count()
        notifications = Announcement.objects.filter(is_active=True).order_by('-created_at')[:5]
        context.update({
            'all_courses': all_courses,
            'total_students': total_students,
            'total_lecturers': total_lecturers,
            'unpaid_total': unpaid_total,
            'unpaid_count': all_fees.count(),
            'total_answers': total_answers,
            'ai_graded': ai_graded,
            'overridden': overridden,
            'all_lecturers': User.objects.filter(role='lecturer'),
            'all_users': User.objects.all().order_by('role'),
            'notifications': notifications,
        })

    if user.role == 'student':
        return render(request, 'accounts/dashboard_student.html', context)
    elif user.role == 'lecturer':
        return render(request, 'accounts/dashboard_lecturer.html', context)
    else:
        return render(request, 'accounts/dashboard_admin.html', context)


def logout_view(request):
    if request.user.is_authenticated:
        _log(request, 'logout', 'login', 'User logged out')
    logout(request)
    return redirect("login")


@login_required(login_url='login')
def profile_view(request):
    user = request.user
    cloudinary_ok = config('CLOUDINARY_CLOUD_NAME', default='placeholder') != 'placeholder'

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name  = request.POST.get('last_name', user.last_name).strip()
        user.phone      = request.POST.get('phone', user.phone).strip()
        user.bio        = request.POST.get('bio', user.bio).strip()
        new_email = request.POST.get('email', user.email).strip()
        if new_email and new_email != user.email:
            if not User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                user.email    = new_email
                user.username = new_email

        update_fields = ['first_name', 'last_name', 'email', 'username', 'phone', 'bio']

        if cloudinary_ok and request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
            update_fields.append('profile_picture')
        elif not cloudinary_ok and request.FILES.get('profile_picture'):
            messages.warning(request, 'Profile picture upload requires Cloudinary keys in .env. Other changes saved.')

        user.save(update_fields=update_fields)
        _log(request, 'update', f'user:{user.email}', 'Profile updated')
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {'user': user, 'cloudinary_ok': cloudinary_ok})


# ── Announcement views ────────────────────────────────────────────────

@login_required(login_url='login')
def post_announcement(request):
    from .models import Announcement
    from apps.courses.models import Course
    if request.user.role not in ('staff', 'lecturer'):
        return redirect('dashboard')
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        body     = request.POST.get('body', '').strip()
        audience = request.POST.get('audience', 'all')
        course_id= request.POST.get('course')
        if title and body:
            ann = Announcement.objects.create(
                title=title, body=body, audience=audience,
                created_by=request.user, is_active=True
            )
            if course_id:
                course = Course.objects.filter(pk=course_id).first()
                if course:
                    ann.course = course
                    ann.save()
            _log(request, 'create', f'announcement:{ann.pk}', f'Posted: {title}')
            messages.success(request, 'Announcement posted successfully.')
        return redirect('dashboard')
    # GET — show form
    if request.user.role == 'lecturer':
        courses = Course.objects.filter(lecturer=request.user)
    else:
        courses = Course.objects.all()
    return render(request, 'accounts/post_announcement.html', {'courses': courses})


# ── Pay fee ───────────────────────────────────────────────────────────

@login_required(login_url='login')
def pay_fee(request, fee_id):
    from apps.finances.models import Fee
    if request.user.role != 'student':
        return redirect('dashboard')
    fee = get_object_or_404(Fee, pk=fee_id, student=request.user)
    if not fee.is_paid:
        fee.is_paid = True
        fee.save()
        _log(request, 'update', f'fee:{fee_id}', f'Fee paid: {fee.get_fee_type_display()}')
        messages.success(request, f'{fee.get_fee_type_display()} of RWF {fee.amount:,.0f} marked as paid!')
    return redirect('dashboard')


# ── Search autocomplete APIs ──────────────────────────────────────────

@login_required(login_url='login')
def search_users_api(request):
    q    = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    if len(q) < 2:
        return JsonResponse({'results': []})
    users = User.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) |
        Q(email__icontains=q) | Q(student_id__icontains=q)
    )
    if role:
        users = users.filter(role=role)
    results = [{'id': u.pk, 'name': u.get_full_name() or u.username,
                'email': u.email, 'role': u.role, 'student_id': u.student_id or ''}
               for u in users[:10]]
    return JsonResponse({'results': results})


@login_required(login_url='login')
def search_courses_api(request):
    from apps.courses.models import Course
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})
    courses = Course.objects.filter(
        Q(title__icontains=q) | Q(code__icontains=q)
    )[:10]
    results = [{'id': c.pk, 'code': c.code, 'title': c.title, 'credits': c.credits,
                'lecturer': c.lecturer.get_full_name() if c.lecturer else 'TBA'}
               for c in courses]
    return JsonResponse({'results': results})


# ── Role area stubs ───────────────────────────────────────────────────

def student_area(request):
    return render(request, 'accounts/dashboard_student.html')


def lecturer_area(request):
    return render(request, 'accounts/dashboard_lecturer.html')


def staff_area(request):
    return render(request, 'accounts/dashboard_admin.html')
