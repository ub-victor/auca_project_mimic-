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

------------------------------------------------------------------------

# Team Members & Roles

  -----------------------------------------------------------------------
  Member         GitHub Username/team               Primary Focus
  -------------- ----------------------------- --------------------------
  Victoire       @ub-victor                     Architecture, code
  (Lead)                                       reviews, deployment,
                                               integration

  Team1                              Authentication, user
  (+250 780 919 720 ~26949 Umutoni Gisele/     profiles, password reset
   +250 791 906 031 Bosco )             

  Team2       Team 2                     Database models,
  (+250 788 426 996 ~Hirwa Roy 24174/     migrations, API structure
   +250 791 761 076 ~26454_clement 
    )                                   

  Team3       Team3                     Frontend (dashboard,
  (+254 790 877089~Anduru/               responsive UI, base templates)     
  +250 782 802 631~Praise Mutijima
  )                                  
                                               

  Team 4       Team4                     Courses, enrollments,
  (+250 793 330 328 ~Josiane🤍/          timetable
  Diane Auca +250 783 829 899          
  )                                  

  Team 5       Team 5                     ML/AI evaluation module,
  (Deborah +250 791 319 715/              assessments
   Valentin +250 793 037 644
  )                                  
  -----------------------------------------------------------------------



------------------------------------------------------------------------

# Detailed Task Assignments

## 🔹 Member 1: Victoire (Team Lead)

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
-   Run initial migrations and test locally.
-   Push branch and open PR with documentation of setup steps.

### Deliverable PR:

Contains working project configuration, Cloudinary ready, custom User
model migrated.

------------------------------------------------------------------------

## 🔹 Member 2: Debora -- Authentication & User Profiles

**Branch:** `feature/auth-debora`

### Tasks:

-   Complete signup, login, logout functionality using Django
    authentication
-   Password reset via email (console backend for development)
-   User profile page (view & edit)
-   Profile picture upload using Cloudinary field
-   Role-based access control (decorators)

### Methodology:

-   Replace demo dict with Django `authenticate()` and `login()`.
-   Use forms.py for validation.
-   Configure password reset using Django built-in views.
-   Create profile.html extending base.html.
-   Allow editing of user fields and profile picture.
-   Create decorators: `@student_required`, `@lecturer_required`.

### Deliverable PR:

Full authentication system with profile management and role-based
access.

------------------------------------------------------------------------

## 🔹 Member 3: Valentin -- Database Models & Core Structure

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

## 🔹 Member 4: Student A -- Frontend & Dashboard

**Branch:** `feature/frontend-studenta`

### Tasks:

-   Create base.html template
-   Refactor templates
-   Move inline styles to CSS
-   Make dashboard dynamic
-   Improve responsiveness
-   Add JS enhancements

### Methodology:

-   Use `{% block content %}`
-   Create main.css and modular CSS
-   Use loops for dynamic data
-   Test responsiveness
-   Add validation and spinners

### Deliverable PR:

Clean responsive UI with dynamic dashboard.

------------------------------------------------------------------------

## 🔹 Member 5: Student B -- Courses & Timetable

**Branch:** `feature/courses-studentb`

### Tasks:

-   Course list view
-   Course detail view
-   Enrollment functionality
-   Timetable generation
-   Lecturer course management

### Methodology:

-   Create views and templates
-   Prevent duplicate enrollment
-   Display timetable grouped by day
-   Add lecturer permissions

### Deliverable PR:

Working course system with enrollment and timetable.

------------------------------------------------------------------------

## 🔹 Member 6: Student C -- Assessments & ML

**Branch:** `feature/ml-studentc`

### Tasks:

-   Assignment creation
-   Submission interface
-   ML evaluation integration
-   Lecturer grading interface
-   Final grading storage

### Methodology:

-   Use formsets for questions
-   Store submissions
-   Integrate Sentence Transformers
-   Save AI scores and feedback
-   Allow lecturer override

### Deliverable PR:

Full assessment system with AI grading support.

------------------------------------------------------------------------

# Additional Tasks

  Task                    Suggested Assignee
  ----------------------- --------------------
  Finance module          Valentin or Debora
  Announcements system    Student A
  Transcript generation   Student B
  API (DRF)               Victoire
  Testing                 All

------------------------------------------------------------------------

# Timeline (6 Weeks)

  Week   Focus                          Members
  ------ ------------------------------ ----------------------
  1      Setup, models, base template   All
  2      Auth & profiles                Debora, Student A
  3      Courses, dashboard             Student B, Student A
  4      Assessments & ML               Student C
  5      Finances & grades              Valentin
  6      Testing & deployment           All

------------------------------------------------------------------------

# Pull Request Template

``` markdown
## Description
Brief summary of changes.

## Related Issue
Link to task (if any).

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
Describe manual tests performed.

## Screenshots (if applicable)

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

-   Communication: Use Slack/Discord/WhatsApp
-   Daily sync:
    -   What I did yesterday
    -   What I will do today
    -   Blockers
-   Help teammates when done early
