# AUCA Project Mimic

A Django-based web application that mimics the AUCA (Adventist University of Central Africa) student portal, featuring a public home page, authentication system, student dashboard, profile management, and Cloudinary integration for media storage.

---

## Table of Contents

- [Authentication System](#authentication-system)
- [How to Run](#how-to-run)
- [URL Routes](#url-routes)
- [Role-Based Access Control](#role-based-access-control)
- [Password Reset](#password-reset)
- [Profile & Picture Upload](#profile--picture-upload)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Running Tests](#running-tests)

---

## Authentication System

- Signup at `/signup/` — creates a real Django user via `SignupForm`
- Login at `/login/` using **email or student ID** (custom `EmailOrStudentIDBackend`)
- Logout at `/logout/`
- Password reset via Django built-in views at `/password-reset/`
- Authentication uses Django's `authenticate()` and `login()` — no demo dictionary

---

## How to Run

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd auca_project_mimic
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** — create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. Open `http://127.0.0.1:8000/`

---

## URL Routes

| URL | View | Name | Description |
|-----|------|------|-------------|
| `/` | `home_view` | `home` | Public home page |
| `/login/` | `login_view` | `login` | Login with email or student ID |
| `/signup/` | `signup_view` | `signup` | Register new account |
| `/logout/` | `logout_view` | `logout` | Clears session, redirects to login |
| `/dashboard/` | `dashboard_view` | `dashboard` | Student dashboard (login required) |
| `/profile/` | `profile_view` | `profile` | View and edit profile (login required) |
| `/forgot-password/` | `forgot_password_view` | `forgot_password` | Custom forgot password page |
| `/password-reset/` | Django built-in | `password_reset` | Real password reset via email |
| `/password-reset/done/` | Django built-in | `password_reset_done` | Confirmation page |
| `/password-reset/confirm/<uidb64>/<token>/` | Django built-in | `password_reset_confirm` | Set new password |
| `/password-reset/complete/` | Django built-in | `password_reset_complete` | Reset complete |
| `/student-area/` | `student_area` | `student_area` | Students + staff only |
| `/lecturer-area/` | `lecturer_area` | `lecturer_area` | Students + lecturers + staff |
| `/staff-area/` | `staff_area` | `staff_area` | Staff only |
| `/admin/` | Django admin | — | Django admin panel |

---

## Role-Based Access Control

Three custom decorators in `apps/accounts/decorators.py`:

| Decorator | Allowed Roles | Description |
|-----------|--------------|-------------|
| `@student_required` | student, staff | Students only |
| `@lecturer_required` | student, lecturer, staff | Manages both students and lecturers |
| `@staff_required` | staff | Full access, staff only |

---

## Password Reset

In development, emails are printed to the **server console** (not sent to inbox).

1. Go to `/password-reset/`
2. Enter your registered email
3. Check the terminal running `runserver` for the reset link
4. Copy the `http://127.0.0.1/password-reset/confirm/.../` URL and open it
5. Set a new password

Configured via:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'     # production
```

---

## Profile & Picture Upload

- Profile page at `/profile/` — edit first name, last name, email, phone, bio
- Profile picture upload via `ImageField`
- In development: files saved to `media/profile_pictures/` (local filesystem)
- In production: files uploaded to Cloudinary via `DEFAULT_FILE_STORAGE`

---

## Project Structure

```
auca_project_mimic/
├── apps/
│   └── accounts/
│       ├── backends.py        # EmailOrStudentIDBackend
│       ├── decorators.py      # student_required, lecturer_required, staff_required
│       ├── forms.py           # SignupForm, ProfileForm
│       ├── models.py          # CustomUser (AbstractUser)
│       ├── migrations/
│       ├── templates/accounts/
│       │   ├── login.html
│       │   ├── signup.html
│       │   ├── dashboard.html
│       │   ├── profile.html
│       │   ├── forgot_password.html
│       │   ├── password_reset_form.html
│       │   ├── password_reset_done.html
│       │   ├── password_reset_confirm.html
│       │   └── password_reset_complete.html
│       ├── urls.py
│       └── views.py
├── auca_project_mimic/
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── static/
│   └── css/
│       ├── style.css
│       └── home.css
├── templates/
│   ├── base.html
│   └── home.html
├── tests/
│   └── test_accounts.py
├── manage.py
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.3 |
| Language | Python 3.12 |
| Database | SQLite (development), PostgreSQL (production) |
| Media Storage | Local filesystem (dev), Cloudinary (production) |
| Auth Backend | Custom `EmailOrStudentIDBackend` |
| Environment | python-decouple |
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Session | Django built-in session framework |

---

## Running Tests

```bash
python manage.py test tests.test_accounts --verbosity=2
```

13 tests covering:
- Signup (creates user, password mismatch, duplicate email)
- Login (valid, invalid, redirect if authenticated)
- Profile (page loads, field update)
- Decorators (role blocking and allowing)

*Last updated: April 25, 2026*
