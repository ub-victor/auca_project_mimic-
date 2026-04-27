# AUCA Project Mimic — Updated Documentation

A Django-based web application that mimics the AUCA (Adventist University of Central Africa) student portal, featuring a login page and a fully designed student dashboard with Cloudinary integration for media storage.

---

## Table of Contents

- [Demo Credentials](#demo-credentials)
- [How to Run](#how-to-run)
- [Cloudinary Integration](#cloudinary-integration)
- [What Was Built](#what-was-built)
  - [Login Page](#1-login-page)
  - [Dashboard — Initial Version](#2-dashboard--initial-version)
  - [Dashboard — Redesign Iterations](#3-dashboard--redesign-iterations)
  - [Final Dashboard](#4-final-dashboard)
- [Project Structure](#project-structure)
- [URL Routes](#url-routes)
- [Tech Stack](#tech-stack)

---

## Authentication & Profile Management

This application now uses Django authentication with a custom `CustomUser` model stored in the database.

- Users can register using the signup page.
- Login uses `django.contrib.auth.authenticate()` and `login()`.
- Password reset is enabled through Django's built-in password reset views and the console email backend for local development.
- Users can edit their profile, including uploading a profile picture to Cloudinary.
- Role-based access control is implemented through decorators: `@student_required`, `@lecturer_required`, and `@staff_required`.

> Use Django admin or the signup page to create accounts; there are no hard-coded in-memory demo credentials in the final auth flow.

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3  # Or PostgreSQL URL
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Upload media files to Cloudinary** (optional, if local media exists):
   ```bash
   python manage.py upload_to_cloudinary
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   Open your browser and go to `http://127.0.0.1:8000/`.

---

## Cloudinary Integration

This project uses Cloudinary for media storage to handle images, favicons, and other static assets efficiently.

### Setup
- Install required packages: `cloudinary`, `django-cloudinary-storage`
- Configure Cloudinary credentials in `.env` file
- Add Cloudinary settings in `auca_project_mimic/settings/base.py`
- Use the management command `upload_to_cloudinary` to migrate local media files to Cloudinary

### Features
- Automatic media URL generation in templates
- Favicon served via Cloudinary
- Secure and scalable media storage

---

## What Was Built

### 1. Login Page

The login page (`accounts/templates/accounts/login.html`) replicates the AUCA portal login interface.

**Features:**
- Email and password input fields
- "I am a staff" checkbox for role selection
- "Forgot Password?" link
- "Sign Up" link for new users
- Responsive layout — left side has the form, right side has a cover image
- On mobile, the right-side image is hidden and the form takes full width
- Error message displayed on invalid credentials

**Authentication flow (`apps/accounts/views.py`):**
- `POST` request validates the login form and authenticates against the database using Django auth.
- On success: logs the user in with `login(request, user)` and redirects to `/dashboard/`.
- On failure: redisplays the login page with validation or credential errors.
- Password reset routes use Django's built-in views and the console email backend in development.
- Profile editing uses a `ProfileForm` to update first name, last name, email, bio, phone, and Cloudinary profile picture.

---

### 2. Dashboard — Initial Version

The first dashboard (`accounts/templates/accounts/dashboard.html`) was a simple layout with:

- A top navbar with the AUCA logo and a logout button
- A welcome card showing the logged-in email and role badge
- Four basic quick-access cards: My Courses, Grades, Schedule, Profile — each with an emoji icon and a short description

---

### 3. Dashboard — Redesign Iterations

The dashboard went through several improvement rounds based on feedback:

#### Iteration 1 — Professional Redesign (Remove Emoji Icons)
- Replaced all emoji icons with colored top-border accent cards
- Added a sticky navbar with a user email pill
- Introduced a stats row (Courses, Avg. Grade, Assignments Due, Current Term)
- Added a two-column panel: Enrolled Courses table + Announcements list
- "AUCA Portal" navbar title made bold white uppercase

#### Iteration 2 — Sample Data & Richer Cards
- Stats row updated with real sample numbers
- Cards converted to a 2×2 grid, each with real content:
  - **Schedule**: compact timetable (day, time, course)
  - **Grades**: per-course grade pills (A/B/C color coded) + Download Transcript button
  - **Enrolled Courses**: course list with credit badges
  - **Profile**: student details with a "View Profile →" link in the card header
- Announcements moved to a full-width panel below the grid

#### Iteration 3 — Grades Simplified + Finances Added
- **Grades card**: stripped grade rows, replaced with a large GPA number (3.6), three meta stats (Avg. Score, Credits, Courses), and a single "Download Transcript" button
- **Finances card** (new): replaced the old plain slot with a fee breakdown table:
  - Tuition Fee — RWF 450,000 — Paid
  - Registration Fee — RWF 25,000 — Paid
  - Library Fee — RWF 10,000 — Due
  - ICT Fee — RWF 15,000 — Due
  - Balance Due total row — RWF 25,000
  - Green "Pay Now" button

#### Iteration 4 — Profile Moved to Navbar
- Profile card removed from the grid entirely
- Profile replaced with a pill button in the navbar showing an avatar circle with initials ("JV") and a "My Profile" label

---

### 4. Final Dashboard

The final dashboard is a full creative redesign with the following structure:

#### Navbar
- Dark background (`#0f1f2e`) for strong contrast
- AUCA logo + "AUCA PORTAL" uppercase title on the left
- Right side: **My Profile** pill button (avatar initials + label) and a ghost **Sign out** link

#### Hero Banner
- Full-width dark-to-navy gradient strip
- Personalized greeting with email and semester info
- Role badge
- Floating stat strip (bottom-right of hero): Courses, GPA, Credits, Due Tasks

#### Row 1 — Academic Overview (3-column grid)

| Card | Content |
|------|---------|
| **Timetable** | Day chip + course name + time for Mon–Fri. Teal left accent. |
| **Enrolled Courses** | Colored dot + course name + credit badge per course. Navy left accent. |
| **Grades** | Circular GPA badge (gradient), stats (Avg Score, Credits, Courses), Download Transcript button. Dark left accent. |

#### Row 2 — Finance & Updates (2-column grid)

| Card | Content |
|------|---------|
| **Finances** | Fee breakdown with Paid/Due pills, bold Balance Due total, teal Pay Now button. Amber left accent. |
| **Announcements** | Teal dot per item, announcement title + date. No accent border. |

#### Sample Data Used

| Field | Value |
|-------|-------|
| Student Name | Jean Valentin |
| Student ID | AUCA-2024-0312 |
| Faculty | Computer Science |
| Year | Year 3 |
| GPA | 3.6 |
| Average Score | 82% |
| Credits | 16 |
| Courses | Intro to Big Data, Web Development, Database Systems, Data Structures, Software Engineering |
| Balance Due | RWF 25,000 |

---

## Project Structure

```
auca_project_mimic/
├── apps/
│   ├── accounts/
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── __pycache__/
│   │   ├── templates/
│   │   │   └── accounts/
│   │   │       ├── dashboard.html
│   │   │       ├── forgot_password.html
│   │   │       ├── login.html
│   │   │       └── signup.html
│   │   ├── urls.py
│   │   └── views.py
│   ├── assessments/
│   │   ├── admin.py
│   │   ├── ai_evaluator.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── __pycache__/
│   │   ├── tests.py
│   │   └── views.py
│   ├── core/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       ├── __pycache__/
│   │   │       └── upload_to_cloudinary.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── __pycache__/
│   │   ├── tests.py
│   │   └── views.py
│   ├── courses/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── __pycache__/
│   │   ├── tests.py
│   │   └── views.py
│   ├── finances/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── __pycache__/
│   │   ├── tests.py
│   │   └── views.py
│   ├── grades/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── __pycache__/
│   │   ├── tests.py
│   │   └── views.py
│   ├── __init__.py
│   └── __pycache__/
├── auca_project_mimic/
│   ├── asgi.py
│   ├── __init__.py
│   ├── __pycache__/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── __init__.py
│   │   ├── production.py
│   │   └── __pycache__/
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── docs/
├── manage.py
├── ml_models/
│   ├── answer_evaluator.pkl
│   └── vectorizer.pkl
├── README.md
├── requirements.txt
├── static/
│   ├── css/
│   │   └── style.css
│   ├── img/
│   └── js/
├── templates/
│   ├── base.html
│   └── includes/
└── utils/
    ├── cloudinary_utils.py
    └── ml_utils.py
```
        ├── fulldesk.png
        └── mobileview.png
```

---

## URL Routes

| URL | View | Name | Description |
|-----|------|------|-------------|
| `/` | `login_view` | `login` | Login page |
| `/dashboard/` | `dashboard_view` | `dashboard` | Student dashboard (session required) |
| `/logout/` | `logout_view` | `logout` | Clears session, redirects to login |
| `/admin/` | Django admin | — | Django admin panel |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0.3 |
| Language | Python 3.12 |
| Database | SQLite (development), PostgreSQL (production) |
| Media Storage | Cloudinary |
| Environment | python-decouple |
| Frontend | HTML5, CSS3 (no external libraries) |
| Session | Django built-in session framework |
| Static files | Django `{% static %}` template tag, Cloudinary for media |

---

## Notes

- No JavaScript frameworks or CSS libraries (Bootstrap, Tailwind, etc.) are used — the entire UI is pure HTML and CSS
- All dashboard data (courses, grades, finances, announcements) is currently static sample data hardcoded in the template
- Authentication uses a simple in-memory dictionary — no Django `User` model or database authentication is implemented yet
- The "My Profile", "Download Transcript", and "Pay Now" buttons link to `#` as placeholders for future implementation
- Cloudinary is integrated for media storage; local media directories (media/, static/uploads/, static/signupimgs/) have been uploaded and removed
- Favicon is served via Cloudinary URLs in templates
- Machine learning models are stored in `ml_models/` directory (answer_evaluator.pkl, vectorizer.pkl) for AI evaluation features

---

## Planned 
- Backend
- Autentication / Authorization
- AI/ML solution
- Advanced Dashbord

*Last updated: April 11, 2026*
