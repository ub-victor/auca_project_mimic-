from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q
from django.utils import timezone
from apps.accounts.models import CustomUser, AuditLog
from apps.accounts.decorators import staff_required


def _log(request, action, target='', detail=''):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()
    AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action, target=target, detail=detail, ip_address=ip or None
    )


# ── User list with search + filter ───────────────────────────────────

@staff_required
def user_list(request):
    q    = request.GET.get('q', '').strip()
    role = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('role', 'first_name')
    if q:
        users = users.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) |
            Q(email__icontains=q) | Q(student_id__icontains=q)
        )
    if role:
        users = users.filter(role=role)
    _log(request, 'view', 'user_list', f'search={q} role={role}')
    return render(request, 'admin_panel/user_list.html', {
        'users': users, 'q': q, 'role_filter': role,
        'total': users.count(),
    })


# ── User detail / edit ────────────────────────────────────────────────

@staff_required
def user_detail(request, pk):
    u = get_object_or_404(CustomUser, pk=pk)
    from apps.courses.models import CourseEnrollment
    from apps.assessments.models import Answer
    enrollments = CourseEnrollment.objects.filter(student=u).select_related('course') if u.role == 'student' else []
    answers     = Answer.objects.filter(student=u).select_related('question__assessment')[:10] if u.role == 'student' else []
    _log(request, 'view', f'user:{u.email}', f'Admin viewed {u.get_full_name()}')
    return render(request, 'admin_panel/user_detail.html', {
        'u': u, 'enrollments': enrollments, 'answers': answers,
    })


# ── Edit user ─────────────────────────────────────────────────────────

@staff_required
def user_edit(request, pk):
    u = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        u.first_name = request.POST.get('first_name', u.first_name)
        u.last_name  = request.POST.get('last_name', u.last_name)
        u.email      = request.POST.get('email', u.email)
        u.username   = u.email
        u.role       = request.POST.get('role', u.role)
        u.student_id = request.POST.get('student_id', u.student_id)
        u.phone      = request.POST.get('phone', u.phone)
        u.is_active  = request.POST.get('is_active') == 'on'
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            u.set_password(new_password)
        u.save()
        _log(request, 'update', f'user:{u.email}', f'Admin updated {u.get_full_name()}')
        messages.success(request, f'{u.get_full_name()} updated successfully.')
        return redirect('admin_panel:user_detail', pk=pk)
    return render(request, 'admin_panel/user_edit.html', {'u': u})


# ── Create user ───────────────────────────────────────────────────────

@staff_required
def user_create(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        role       = request.POST.get('role', 'student')
        student_id = request.POST.get('student_id', '').strip()
        password   = request.POST.get('password', '').strip()

        if not all([first_name, email, password]):
            messages.error(request, 'First name, email and password are required.')
            return render(request, 'admin_panel/user_create.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, f'Email {email} already exists.')
            return render(request, 'admin_panel/user_create.html')

        u = CustomUser.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
            role=role, student_id=student_id
        )
        _log(request, 'create', f'user:{email}', f'Admin created {u.get_full_name()} as {role}')
        messages.success(request, f'Account created for {u.get_full_name()}.')
        return redirect('admin_panel:user_detail', pk=u.pk)
    return render(request, 'admin_panel/user_create.html')


# ── Impersonate user ──────────────────────────────────────────────────

@staff_required
def impersonate(request, pk):
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, pk=pk)
        _log(request, 'impersonate', f'user:{target_user.email}',
             f'Admin {request.user.email} impersonated {target_user.email}')
        # Store original admin in session
        request.session['impersonating_as'] = target_user.pk
        request.session['original_admin']   = request.user.pk
        auth_login(request, target_user, backend='django.contrib.auth.backends.ModelBackend')
        messages.warning(request, f'You are now logged in as {target_user.get_full_name()}. Go to dashboard to see their view.')
        return redirect('dashboard')
    return redirect('admin_panel:user_detail', pk=pk)


@login_required(login_url='login')
def stop_impersonate(request):
    original_pk = request.session.get('original_admin')
    if original_pk:
        admin_user = get_object_or_404(CustomUser, pk=original_pk)
        del request.session['impersonating_as']
        del request.session['original_admin']
        auth_login(request, admin_user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Returned to admin account.')
    return redirect('dashboard')


# ── Audit log ─────────────────────────────────────────────────────────

@staff_required
def audit_log(request):
    q      = request.GET.get('q', '').strip()
    action = request.GET.get('action', '')
    logs   = AuditLog.objects.select_related('user').all()
    if q:
        logs = logs.filter(
            Q(user__email__icontains=q) | Q(target__icontains=q) | Q(detail__icontains=q)
        )
    if action:
        logs = logs.filter(action=action)
    logs = logs[:500]
    return render(request, 'admin_panel/audit_log.html', {
        'logs': logs, 'q': q, 'action_filter': action,
        'action_choices': AuditLog.ACTION_CHOICES,
    })


# ── PDF Reports ───────────────────────────────────────────────────────

@staff_required
def pdf_audit_log(request):
    logs = AuditLog.objects.select_related('user').all()[:500]
    lines = [
        'AUCA PORTAL — AUDIT LOG REPORT',
        f'Generated: {timezone.now():%Y-%m-%d %H:%M}',
        '=' * 70,
        f'{"Timestamp":<22} {"User":<30} {"Action":<14} {"Target":<25}',
        '-' * 70,
    ]
    for log in logs:
        user_str = log.user.email if log.user else 'Anonymous'
        lines.append(f'{str(log.timestamp)[:19]:<22} {user_str:<30} {log.action:<14} {log.target[:24]:<25}')
    lines += ['', '=' * 70, 'End of Report']
    content = '\n'.join(lines)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="audit_log.txt"'
    return response


@staff_required
def pdf_users(request):
    role = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('role', 'first_name')
    if role:
        users = users.filter(role=role)
    lines = [
        'AUCA PORTAL — USER REPORT',
        f'Generated: {timezone.now():%Y-%m-%d %H:%M}',
        f'Filter: {role or "All roles"}',
        '=' * 70,
        f'{"Name":<25} {"Email":<35} {"Role":<12} {"Student ID":<15}',
        '-' * 70,
    ]
    for u in users:
        lines.append(f'{u.get_full_name()[:24]:<25} {u.email[:34]:<35} {u.role:<12} {u.student_id or "—":<15}')
    lines += ['', f'Total: {users.count()} users', '=' * 70]
    content = '\n'.join(lines)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="users_report.txt"'
    return response
