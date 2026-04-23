# AUCA Project Mimic

A Django-based web application mimicking the AUCA (Adventist University of Central Africa) student portal. Features a public university homepage, full authentication system, student dashboard, and profile management with Cloudinary image storage.

---

## Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd auca_project_mimic
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Required variables:
```env
DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
SECRET_KEY=your-secret-key-here
DEBUG=True
```

> Generate a secret key with:
> `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Run the development server
```bash
python manage.py runserver
```

### 7. Open in browser
```
http://127.0.0.1:8000/
```

---

## URL Routes

| URL | Description |
|-----|-------------|
| `/` | AUCA public homepage |
| `/login/` | Login with email or student ID |
| `/signup/` | Create a new student account |
| `/forgot-password/` | Password reset (prints to terminal in dev) |
| `/dashboard/` | Student dashboard (login required) |
| `/profile/` | View and edit profile + upload picture |
| `/logout/` | Logout and redirect to login |
| `/admin/` | Django admin panel |
| `/password-reset/` | Django built-in password reset flow |

---

## Features

- Public AUCA homepage with campus images served from Cloudinary
- Full authentication — signup, login, logout using Django's auth system
- Login with email OR student ID
- Password reset via email (prints to terminal in development)
- Student dashboard with timetable, courses, grades, finances, announcements
- Profile page — edit name, bio, student ID, upload profile picture to Cloudinary
- Role-based access decorators — `@student_required`, `@lecturer_required`, `@staff_required`
- Custom email authentication backend
- Split settings — `base.py`, `development.py`, `production.py`
- PostgreSQL via NeonDB (falls back to SQLite if no DATABASE_URL)

---

## Project Structure

```
auca_project_mimic/
├── apps/
│   ├── accounts/         # Auth, profiles, decorators
│   ├── assessments/      # Assignments & ML evaluation (in progress)
│   ├── core/             # Shared utilities
│   ├── courses/          # Course management (in progress)
│   ├── finances/         # Finance module (in progress)
│   ├── grades/           # Grades (in progress)
│   └── home/             # Public AUCA homepage
├── auca_project_mimic/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   └── urls.py
├── static/
│   └── css/
├── templates/
│   └── base.html
├── .env.example
├── manage.py
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.0.3 |
| Language | Python 3.x |
| Database | PostgreSQL (NeonDB) / SQLite fallback |
| Media & Static | Cloudinary |
| Environment | python-decouple |
| Frontend | HTML5, CSS3 (no frameworks) |

---

## Notes

- The `.env` file is **not committed** — each developer needs their own
- Dashboard data (courses, grades, finances) is currently static sample data — will be dynamic once other teams complete their modules
- Images on the homepage are served from Cloudinary so everyone sees them without local files

*Last updated: April 2026*
