# AUCA Project Mimic — Updated Documentation

A Django-based web application that mimics the AUCA (Adventist University of Central Africa) student portal, featuring a login page and a fully designed student dashboard.

---

## Table of Contents

- [Demo Credentials](#demo-credentials)
- [How to Run](#how-to-run)
- [What Was Built](#what-was-built)
  - [Login Page](#1-login-page)
  - [Dashboard — Initial Version](#2-dashboard--initial-version)
  - [Dashboard — Redesign Iterations](#3-dashboard--redesign-iterations)
  - [Final Dashboard](#4-final-dashboard)
- [Project Structure](#project-structure)
- [URL Routes](#url-routes)
- [Tech Stack](#tech-stack)

---

## Demo Credentials

Two demo accounts are available. No registration is required — use these directly on the login page.

| Role    | Email                   | Password     |
|---------|-------------------------|--------------|
| Student | student@auca.ac.rw      | student123   |
| Staff   | staff@auca.ac.rw        | staff123     |

> These credentials are defined in `accounts/views.py` under `DEMO_USERS`. No database is used for authentication — it is a simple in-memory dictionary for demo purposes.

---

## How to Run

```bash
# 1. Activate virtual environment
# Windows
py312-env\Scripts\activate

# Linux / Mac
source py312-env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Start the server
python manage.py runserver
```

Then open your browser at:

- **Login page**: `http://127.0.0.1:8000/`
- **Dashboard**: `http://127.0.0.1:8000/dashboard/` *(redirects to login if not authenticated)*
- **Admin panel**: `http://127.0.0.1:8000/admin/`

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

**Authentication flow (`accounts/views.py`):**
- `POST` request checks email and password against `DEMO_USERS`
- On success: stores `user_email` and `user_role` in the Django session, redirects to `/dashboard/`
- On failure: re-renders the login page with an error message
- `GET` request: renders the empty login form

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
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md                          # Original documentation
├── READMEUpdated.md                   # This file
│
├── auca_project_mimic/
│   ├── settings.py
│   ├── urls.py                        # Includes accounts.urls
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── templates/
│   │   └── accounts/
│   │       ├── login.html             # Login page
│   │       └── dashboard.html        # Student dashboard (final redesign)
│   ├── views.py                       # login_view, dashboard_view, logout_view
│   ├── urls.py                        # URL patterns for accounts app
│   ├── models.py
│   ├── admin.py
│   └── apps.py
│
└── static/
    ├── css/
    │   └── style.css                  # Login page styles
    └── img/
        ├── 10001.png                  # AUCA logo
        ├── 10002.jpg                  # Login page cover image
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
| Language | Python 3.8+ |
| Database | SQLite (development) |
| Frontend | HTML5, CSS3 (no external libraries) |
| Session | Django built-in session framework |
| Static files | Django `{% static %}` template tag |

---

## Notes

- No JavaScript frameworks or CSS libraries (Bootstrap, Tailwind, etc.) are used — the entire UI is pure HTML and CSS
- All dashboard data (courses, grades, finances, announcements) is currently static sample data hardcoded in the template
- Authentication uses a simple in-memory dictionary — no Django `User` model or database authentication is implemented yet
- The "My Profile", "Download Transcript", and "Pay Now" buttons link to `#` as placeholders for future implementation

---

## Planned Next Steps

- [ ] Debora — Registration form implementation
- [ ] Valentin — Sign up functionality
- [ ] Connect dashboard data to a real database model
- [ ] Implement Django `User` model authentication
- [ ] Build out Profile, Transcript download, and Payment pages

---

*Last updated: June 2025*
