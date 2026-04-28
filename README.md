# AUCA Project Mimic — Updated Documentation

A Django-based web application that mimics the AUCA (Adventist University of Central Africa) student portal, featuring authentication, dashboard, course management, and AI-powered assessment evaluation.

---

## Table of Contents

- [Demo Credentials](#demo-credentials)
- [How to Run](#how-to-run)
- [Cloudinary Integration](#cloudinary-integration)
- [AI Assessment Evaluation](#ai-assessment-evaluation)
- [What Was Built](#what-was-built)
  - [Authentication & Profile Management](#authentication--profile-management)
  - [Dashboard](#dashboard)
  - [Courses & Timetable Management](#courses--timetable-management)
  - [Assessments & AI Evaluation](#assessments--ai-evaluation)
- [Project Structure](#project-structure)
- [URL Routes](#url-routes)
- [Tech Stack](#tech-stack)

---

## Demo Credentials

- **Admin User**: Username: `admin`, Email: `admin@auca.edu`, Password: `admin@123!`
- Create additional users via signup or Django admin.

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

6. **Create superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Upload media files to Cloudinary** (optional, if local media exists):
   ```bash
   python manage.py upload_to_cloudinary
   ```

8. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:
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

## AI Assessment Evaluation

The application features an AI-powered assessment evaluation system using Sentence Transformers for automated grading and feedback.

### Features
- **Automated Scoring**: Uses semantic similarity to compare student answers with reference answers
- **Feedback Generation**: Provides detailed AI feedback based on similarity scores
- **Lecturer Override**: Lecturers can review AI suggestions and assign final grades
- **File Upload Support**: Students can submit text files or PDFs, automatically extracted
- **Similarity Detection**: Identifies potential plagiarism through text similarity analysis

### Technical Implementation
- **ML Model**: Sentence Transformers (`all-MiniLM-L6-v2`) for embedding and similarity calculation
- **Singleton Pattern**: Model loaded once to avoid repeated initialization overhead
- **Batch Processing**: Supports evaluating multiple answers efficiently
- **Database Storage**: AI scores, similarity percentages, and feedback stored in Submission model

### Workflow
1. Lecturer creates assessment with questions and reference answers
2. Students submit answers via text input or file upload
3. AI evaluates submissions immediately upon submission
4. Lecturers review AI suggestions and can override grades
5. Final grades and feedback are recorded

---

## What Was Built

### Authentication & Profile Management

This application uses Django authentication with a custom `CustomUser` model stored in the database.

- Users can register using the signup page.
- Login uses `django.contrib.auth.authenticate()` and `login()`.
- Password reset is enabled through Django's built-in password reset views and the console email backend for local development.
- Users can edit their profile, including uploading a profile picture to Cloudinary.
- Role-based access control is implemented through decorators: `@student_required`, `@lecturer_required`, and `@staff_required`.

---

### Dashboard

The dashboard provides a comprehensive overview of student information with role-based access.

#### Features
- **Personalized Welcome**: Displays user name, email, and role
- **Academic Stats**: Courses enrolled, GPA, credits, due tasks
- **Timetable**: Weekly schedule with course details
- **Enrolled Courses**: List of current courses with credits
- **Grades Overview**: GPA display with download transcript option
- **Finances**: Fee breakdown and payment status
- **Announcements**: Latest campus updates

#### Responsive Design
- Mobile-first approach with adaptive layouts
- Card-based design with accent colors
- Accessible with ARIA labels and semantic HTML

---

### Courses & Timetable Management

The application includes comprehensive course browsing, enrollment, and timetable functionality.

#### Features Implemented

##### Course List View (`/courses/`)
- **Browse Available Courses**: Paginated grid layout with course cards
- **Advanced Filtering**: Filter by department, semester, and search by course code/title
- **Course Information**: Displays code, title, credits, department, lecturer, and description
- **Responsive Design**: Mobile-friendly grid that adapts to screen size

##### Course Detail View (`/courses/<id>/`)
- **Detailed Course Information**: Complete course details, schedule, and enrollment status
- **Schedule Display**: Shows class times and rooms grouped by day
- **Enrollment Management**: Students can enroll/unenroll with duplicate prevention
- **Role-Based Access**: Different views for students, lecturers, and staff

##### Enrollment Functionality
- **Duplicate Prevention**: Unique constraint prevents multiple enrollments in same course-semester
- **Real-time Status**: Shows current enrollment status and enrollment date
- **Secure Operations**: POST requests with CSRF protection and user validation

##### Timetable Generation (`/courses/timetable/`)
- **Weekly Schedule**: Displays enrolled courses grouped by day of week
- **Time Slots**: Shows start/end times for each class
- **Course Details**: Includes course code, title, room, and lecturer information
- **Current Semester**: Only shows schedules for the active semester

##### Lecturer Course Management (`/courses/lecturer/`)
- **Assigned Courses**: View all courses taught by the lecturer
- **Enrollment Counts**: See number of students enrolled per course
- **Current Semester Focus**: Highlights active semester enrollments

##### User Management (`/courses/users/`) - Staff Only
- **User Overview**: List all users with role-based filtering
- **Search Functionality**: Search by username, email, or name
- **Role Management**: View and manage user roles (Student/Lecturer/Staff)
- **Status Tracking**: Active/inactive user status display

#### Technical Implementation

##### Views & Logic
- **Role-Based Permissions**: Decorators ensure proper access control
- **Database Queries**: Optimized with select_related/prefetch_related for performance
- **Form Validation**: Django forms with custom validation and error handling
- **Pagination**: Efficient handling of large course/user lists

##### Templates & UI
- **Consistent Design**: Extends base.html with shared navigation
- **External CSS**: Dedicated `courses.css` for course-specific styling
- **Responsive Layouts**: Mobile-first design with flexible grids
- **Accessibility**: ARIA labels and semantic HTML structure

##### Models & Relationships
- **CourseSchedule**: New model for managing class schedules
- **Unique Constraints**: Prevents scheduling conflicts and duplicate enrollments
- **Foreign Key Relationships**: Proper linking between courses, users, and semesters

---

### Assessments & AI Evaluation

The assessments module provides a complete assignment submission and evaluation system with AI assistance.

#### Features

##### Assessment Creation
- **Lecturer Interface**: Create assignments with multiple questions using inline formsets
- **Question Management**: Add questions with reference answers for AI evaluation
- **Flexible Assessment Types**: Quiz, Midterm, Final, Assignment support
- **Due Date Management**: Set deadlines and track submission status

##### Student Submission
- **Multi-Question Support**: Submit answers for each question individually
- **File Upload**: Support for text/PDF file submissions with automatic text extraction
- **Validation**: Ensures answers are provided (text or file)
- **Duplicate Prevention**: Students can only submit once per assessment

##### AI Evaluation System
- **Semantic Similarity**: Uses Sentence Transformers to compare answers
- **Automated Scoring**: Generates AI scores (0-100) based on similarity
- **Feedback Generation**: Provides contextual feedback based on similarity levels
- **Similarity Detection**: Identifies potential plagiarism through text analysis
- **Batch Processing**: Efficient evaluation of multiple questions

##### Lecturer Grading Interface
- **Review Submissions**: View all student submissions with AI suggestions
- **Override Grades**: Lecturers can accept or modify AI-recommended grades
- **Feedback Addition**: Add personal feedback alongside AI suggestions
- **Status Management**: Mark submissions as graded or pending

#### Technical Implementation

##### Models
- **Assessment**: Main assessment with questions and metadata
- **Question**: Individual questions with reference answers
- **Submission**: Student submissions with AI evaluation results
- **Answer**: Individual answers linked to submissions

##### AI Evaluator (`apps/assessments/ai_evaluator.py`)
- **AnswerEvaluator Class**: Singleton pattern for model loading
- **Similarity Calculation**: Cosine similarity between embeddings
- **Feedback Mapping**: Score-based feedback generation
- **Batch Evaluation**: Process multiple pairs efficiently

##### Views & Forms
- **Formsets**: Django inline formsets for question management
- **Role-Based Access**: Decorators for student/lecturer permissions
- **File Processing**: PDF and text file extraction using pypdf
- **AJAX Endpoints**: API for evaluation testing

##### Templates & UI
- **Assessment Cards**: Grid layout for assessment browsing
- **Submission Forms**: Multi-question forms with file upload
- **Review Interface**: Detailed submission review with AI insights
- **Responsive Design**: Mobile-friendly assessment pages

#### URL Routes
- `/assessments/` - Assessment list
- `/assessments/create/` - Create new assessment
- `/assessments/<id>/` - Assessment details
- `/assessments/<id>/submit/` - Submit answers
- `/assessments/me/` - Student submissions
- `/assessments/submissions/` - All submissions (lecturer)
- `/assessments/submission/<id>/` - Review submission

---

## Project Structure

```
auca_project_mimic/
├── auca_project_mimic/          # Main Django project
│   ├── settings/
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Dev settings
│   │   └── production.py       # Prod settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py
├── apps/                       # Django apps
│   ├── accounts/               # Authentication & profiles
│   ├── assessments/            # AI-powered assessments
│   ├── core/                   # Core models (Semester, Faculty, etc.)
│   ├── courses/                # Course management
│   ├── finances/               # Fee management
│   └── grades/                 # Grade tracking
├── static/                     # Static files
│   ├── css/
│   │   ├── main.css           # Global styles
│   │   ├── auth.css           # Auth pages
│   │   ├── dashboard.css      # Dashboard
│   │   ├── courses.css        # Courses
│   │   └── assessments.css    # Assessments
│   └── js/
│       └── main.js            # Global JS
├── templates/                  # HTML templates
│   ├── base.html              # Base layout
│   └── admin_dashboard.html
├── utils/                      # Utility functions
├── ml_model/                   # ML utilities (legacy)
└── requirements.txt            # Python dependencies
```

---

## URL Routes

### Authentication
- `/` → Redirects to `/dashboard/`
- `/login/` → Login page
- `/signup/` → Registration
- `/logout/` → Logout
- `/password-reset/` → Password reset flow
- `/profile/` → Profile management

### Dashboard
- `/dashboard/` → Main dashboard

### Courses
- `/courses/` → Course catalog
- `/courses/<id>/` → Course details
- `/courses/<id>/enroll/` → Enroll in course
- `/courses/<id>/unenroll/` → Unenroll from course
- `/courses/timetable/` → Student timetable
- `/courses/lecturer/` → Lecturer courses
- `/courses/users/` → User management (staff)

### Assessments
- `/assessments/` → Assessment list
- `/assessments/create/` → Create assessment
- `/assessments/<id>/` → Assessment details
- `/assessments/<id>/submit/` → Submit answers
- `/assessments/me/` → My submissions
- `/assessments/submissions/` → All submissions
- `/assessments/submission/<id>/` → Review submission
- `/assessments/evaluate/` → AI evaluation API

### Admin
- `/admin/` → Django admin

---

## Tech Stack

- **Backend**: Django 6.0.3, Python 3.12
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Django Auth with custom user model
- **Media Storage**: Cloudinary
- **AI/ML**: Sentence Transformers, PyTorch
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Ready for Heroku/AWS/GCP

---

## Deployment

The application is production-ready with:
- Environment-based configuration
- Cloudinary for media
- PostgreSQL support
- Static file serving
- Security settings in production.py

For deployment:
1. Set `DEBUG=False` in production
2. Configure PostgreSQL DATABASE_URL
3. Set up Cloudinary credentials
4. Run `python manage.py collectstatic`
5. Deploy to your preferred platform


## Database Models & Core Structure

The application uses a comprehensive database schema with the following models:

### Core App
- **Faculty**: Represents academic faculties (e.g., Faculty of Science and Technology)
- **Department**: Departments within faculties (e.g., Computer Science)
- **Semester**: Academic semesters with start/end dates

### Courses App
- **Course**: Course details including code, title, credits, department, lecturer
- **CourseSchedule**: Class schedules with day, time, room for each course-semester
- **CourseEnrollment**: Student enrollments in courses for specific semesters

### Assessments App
- **Assessment**: Exams, quizzes, assignments with due dates and marks
- **Question**: Individual questions within assessments
- **Answer**: Student submissions for questions

### Finances App
- **Fee**: Various fees (tuition, registration, etc.) per student and semester
- **Payment**: Payment records linked to multiple fees

### Grades App
- **Grade**: Final grades for course enrollments with GPA points

### Relationships
- All user-related models use `AUTH_USER_MODEL = 'accounts.CustomUser'`
- Foreign keys establish proper relationships (e.g., Course -> Department, Enrollment -> Student/Course)
- Many-to-many relationships for courses and semesters, payments and fees

### Admin Interface
All models are registered in Django admin with:
- `list_display` for key fields
- `search_fields` for quick lookup
- `list_filter` for filtering options

### Sample Data
Sample data has been populated including:
- Demo users (student, lecturer, staff)
- Faculty, department, semester
- Courses, enrollments, assessments, grades, fees, payments

Run `python manage.py populate_sample_data` to reload sample data.

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

## Implementation Status

### Completed Features
- ✅ **Authentication System**: Custom user model with roles, signup/login/logout, password reset, profile management with Cloudinary integration.
- ✅ **Database Models**: Comprehensive schema with all apps (core, courses, assessments, finances, grades) and proper relationships.
- ✅ **Admin Interface**: All models registered with list_display, search_fields, and list_filter.
- ✅ **Migrations**: Database schema created and migrations applied.
- ✅ **Sample Data**: Management command to populate demo users, faculties, courses, enrollments, assessments, grades, fees, and payments.
- ✅ **GitHub Deployment**: Code pushed to GitHub repository on the `develop` branch.

### System Robustness
- **Relationships**: All foreign keys, one-to-one, and many-to-many relationships properly defined.
- **Validation**: Django forms used for input validation and error handling.
- **Security**: Role-based access control with decorators, Django auth for secure authentication.
- **Scalability**: Modular app structure, Cloudinary for media storage, configurable database backends.
- **Maintainability**: Clear model definitions, admin interfaces, and comprehensive documentation.

### Next Steps
The system is now ready for further development, such as:
- Implementing views for courses, assessments, grades, and finances.
- Adding API endpoints for mobile app integration.
- Enhancing the dashboard with real-time data.
- Deploying to production with PostgreSQL and proper environment configuration.

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
