# AUCA Project Mimic -- Team Workflow & Task Assignment

This document outlines the complete workflow, branch strategy, and
specific task assignments for different team members. Follow this guide
strictly to ensure smooth collaboration and timely completion.

------------------------------------------------------------------------

# Git Workflow & Branching Strategy

We will use GitHub Flow with a develop branch as integration point.

## Branch Structure

    main                 # Production-ready code (deployed)
      └── develop        # Integration branch (all features merge here)
           ├── feature/auth-<name>        # Authentication features
           ├── feature/models-<name>      # Database models
           ├── feature/dashboard-<name>   # Dashboard & UI
           ├── feature/courses-<name>     # Course management
           ├── feature/assessments-<name> # Assignments & ML
           ├── feature/finances-<name>    # Finance module
           └── feature/ml-<name>          # ML evaluation

## Rules

-   Never commit directly to main or develop.
-   Create a feature branch from develop for each task.
-   Branch naming convention: `feature/<module>-<your-name>` (e.g.,
    `feature/auth-debora`).
-   Commit frequently with clear messages:
    -   `feat: add login form validation`
    -   `fix: correct course credit calculation`
-   After completing a task, open a Pull Request (PR) to develop.

### PR must include:

-   Description of changes
-   Screenshots (if UI related)
-   Checklist of completed items
-   Any notes for reviewers
-   When you PR conflit fix the error or get in touch with the branch it conflits with so you can resolve the error

Team lead(i) reviews and merges PRs(some time someone else can do it, we're leader).

# Team Members & Roles

| # | Member | Phone | Team | Primary Focus |
|---|--------|-------|------|----------------|
| 1 | Victoire (Lead) | +250-79-44-12-876 | Team 0 | Architecture, code reviews, deployment, integration |
| 2 | Umutoni Gisele | +250 780 919 720 | Team 1 | Authentication, user profiles, password reset |
| 3 | Bosco | +250 791 906 031 | Team 1 | Authentication, user profiles, password reset |
| 4 | Hirwa Roy | +250 788 426 996 | Team 2 | Database models, migrations, API structure |
| 5 | Clement | +250 791 761 076 | Team 2 | Database models, migrations, API structure |
| 6 | Anduru | +254 790 877 089 | Team 3 | Frontend (dashboard, responsive UI, base templates) |
| 7 | Praise Mutijima | +250 782 802 631 | Team 3 | Frontend (dashboard, responsive UI, base templates) |
| 8 | Josiane | +250 793 330 328 | Team 4 | Courses, enrollments, timetable |
| 9 | Diane Auca | +250 783 829 899 | Team 4 | Courses, enrollments, timetable |
| 10 | Deborah | +250 791 319 715 | Team 5 | ML/AI evaluation module, assessments |
| 11 | Valentin | +250 793 037 644 | Team 5 | ML/AI evaluation module, assessments |

------------------------------------------------------------------------


# Detailed Task Assignments

## 🔹 Team 0: Victoire (Team Lead)

**Branch:** `feature/setup-victoire(merged and deleted)`

### Responsibilities:

-   Project setup (split settings, environment variables)
-   Cloudinary integration for file uploads
-   Overall architecture guidance
-   Review and merge PRs
-   Deployment configuration

### Methodology:

-   Create develop branch from main.
-   Set up settings/ directory with base.py, development.py,
    production.py.
-   Install python-decouple, configure .env file (add to .gitignore).
-   Integrate Cloudinary: add to INSTALLED_APPS, configure storage, test
    image upload.
-   Create base accounts app structure and custom User model (extend
    AbstractUser).
-   Run initial migrations and test locally(I test the connect added randomly 100 tables).
-   Push branch and open PR with documentation of setup steps.

### Deliverable PR:

Contains working project configuration, Cloudinary ready,Progress Bb(NeonTech) custom User
model migrated.

------------------------------------------------------------------------

## 🔹 Team 1: (+250 780 919 720 ~26949 Umutoni Gisele/ +250 791 906 031 Bosco ) -- Authentication & User Profiles

**Branch:** `feature/auth-<name>`

### Tasks:

-   Complete signup, login, logout functionality using Django
    authentication
-   Password reset via email (console backend for development)
-   User profile page (view & edit)
-   Profile picture upload using Cloudinary field
-   Role-based access control (decorators for student/staff/lecturer)

### Methodology:

-   Replace demo dict with Django `authenticate()` and `login()`.
-   Use forms.py for validation.
-   Configure password reset using Django built-in views.
-   Create profile.html extending base.html.
-   Allow editing of user fields and profile picture.
-   Create decorators: `@student_required`, `@lecturer_required` and a `@lecturer_required` who will manage both Student/ lectures .

### Deliverable PR:

Full authentication system with profile management and role-based
access.

------------------------------------------------------------------------

## 🔹 Team 2: (+250 788 426 996 ~Hirwa Roy 24174/ +250 791 761 076 ~26454_clement ) -- Database Models & Core Structure

**Branch:** `feature/models-valentin`

### Tasks:

-   Create all model classes
-   Set relationships (FK, O2O, M2M)
-   Run migrations
-   Register models in admin

### Methodology:

-   Create apps inside apps/
-   Define models per schema
-   Use `AUTH_USER_MODEL = 'accounts.User'`
-   Register admin with list_display and search_fields
-   Populate sample data

### Deliverable PR:

All models, migrations, admin working with sample data.

------------------------------------------------------------------------

## 🔹 Team 3: (+254 790 877089~Anduru/+250 782 802 631~Praise Mutijima) -- Frontend & Dashboard

**Branch:** `feature/frontend-studenta`

### Tasks:

-   Create base.html template with blocks (title, content, extra_css, extra_js)
-   Refactor all existing templates (login.html, signup.html, forgot_password.html, dashboard.html) to extend base.html
-   Move inline styles to external CSS files (e.g., css/dashboard.css, css/auth.css)
-   Make dashboard dynamic: replace static sample data with real data from context (passed from views)
-   Improve mobile responsiveness for all pages
-   Add JavaScript enhancements (form validation, AJAX for smoother UX where needed)

### Methodology:

-   Use `{% block content %}`
-   Create main.css and modular CSS
-   Use loops for dynamic data
-   Test responsiveness
-   Add validation and spinners

### Deliverable PR:

Clean responsive UI with dynamic dashboard.

------------------------------------------------------------------------

## 🔹 Team 4: (+250 793 330 328 ~Josiane🤍/Diane Auca +250 783 829 899) -- Courses & Timetable

**Branch:** `feature/courses-studentb`

### Tasks:

-   Course list view
-   Course detail view
-   Enrollment functionality
-   Timetable generation
-   Lecturer course management
-   Upper User Full Management

### Methodology:

-   Create views and templates
-   Prevent duplicate enrollment
-   Display timetable grouped by day
-   Add all Users permissions (Students/Admins/Lectures)

### Deliverable PR:

Working course system with enrollment and timetable.

------------------------------------------------------------------------

## 🔹 Team 5: (Deborah +250 791 319 715 / Valentin +250 793 037 644
  ) -- Assessments & ML

**Branch:** `feature/ml-studentc`

### Tasks:

-   **Assignment Creation:** Build form for lecturer to add assignment with multiple questions. Use inline formsets for questions.
-   **Submission:** Student can view assignments, submit answers via textarea or file (file upload to Cloudinary). Use Submission model.
-   **ML evaluation integration**
    - Install sentence-transformers.
    - Create ai_evaluator.py with AnswerEvaluator class (as per plan).
    - In submission view, after saving, call evaluator and store ai_score, similarity_score, ai_feedback.
    - (Note: Loading the model per request is slow; consider loading once in app config or using a singleton.)
-   **Grading Interface:** For lecturers, display submission details, AI suggestion, and a form to input final grade and feedback.
-   **Testing:** Test with sample answers; adjust similarity threshold mapping.
### Methodology:

-   Use formsets for questions
-   Store submissions
-   Integrate Sentence Transformers
-   Save AI scores and feedback
-   Allow lecturer override

### Deliverable PR:
Complete assessment flow with AI evaluation; lecturer can see AI suggestions and override grades.

------------------------------------------------------------------------

# Additional Tasks

  Task                    Suggested Assignee
  ----------------------- --------------------
  Finance module          Team 4
  Announcements system    Team 3
  Transcript generation   Team 2
  API (DRF)               Team 1
  Testing                 All of us

------------------------------------------------------------------------

# Timeline (Everyday work on this Project like is the deadline is tomorrow)

  Priority   Focus                          
  ------     ------------------------------ 
  1          Setup, models, base template   
  2          Auth & profiles                
  3          Courses, dashboard             
  4          Assessments & ML               
  5          Finances & grades              
  6          Testing & deployment        

------------------------------------------------------------------------

# Pull Request Template

``` markdown
## Description
Brief summary of changes.

## Related Issue
Link to task (if any).
all alway Update the Readme so it can stay Updated

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
Describe manual tests performed.

## Screenshots (if applicable[Optional])

## Checklist
- [ ] My code follows the project's style guidelines.
- [ ] I have performed a self-review.
- [ ] I have commented my code where necessary.
- [ ] I have updated the documentation.
- [ ] My changes generate no new warnings.
- [ ] I have added tests that prove my fix/feature works.
```

------------------------------------------------------------------------

# Final Notes
- We will use our WhatsApp group for Updates and communication
**Love y'all guys, lets do this with all our heart**
