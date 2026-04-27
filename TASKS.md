# AUCA Project Mimic -- Team Workflow & Task Assignment

This document outlines the complete workflow, branch strategy, and
specific task assignments for different team members. Follow this guide
strictly to ensure smooth collaboration and timely completion.

------------------------------------------------------------------------

# Git Workflow & Branching Strategy

We will use GitHub Flow with a develop branch as integration point.
Team members may need to share a single branch identified by their team number.

## Branch Structure

    main                 # Production-ready code (deployed)
      └── develop        # Integration branch (all features merge here)
           ├── feature/auth-team1        # Authentication features
           ├── feature/models-team2      # Database models
           ├── feature/dashboard-team3   # Dashboard & UI
           ├── feature/courses-team4     # Course management
           ├── feature/assessments-team5 # Assignments & ML
           ├── feature/finances-team4    # Finance module
           └── feature/ppt-team7         # PPT presentations

## Rules

-   Never commit directly to main or develop.
-   Create a feature branch from develop for each task.
-   Branch naming convention: `feature/<module>-team#` (e.g.,
    `feature/auth-team1`).
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
# Team Members & Roles

|  #   | Member                                   | Phone                                      |  Team  | Primary Focus                                              |
|:----:|------------------------------------------|--------------------------------------------:|:------:|------------------------------------------------------------|
|  1   | Victoire (Lead)                          |                          +250-79-44-12-876 | Team 0 | Architecture, code reviews, deployment, integration        |
| 2-4  | Umutoni Gisele, Bosco, Tuyishime         | +250 780 919 720, +250 791 906 031, 26717  | Team 1 | Authentication, user profiles, password reset              |
| 5-7  | Hirwa Roy, Clement, Mugisha              | +250 788 426 996, +250 791 761 076, 27891  | Team 2 | Database models, migrations, API structure                 |
| 8-10 | Anduru, Praise Mutijima, Barema          | +254 790 877 089, +250 782 802 631, 26255  | Team 3 | Frontend (dashboard, responsive UI, base templates)        |
|11-13 | Josiane, Diane Auca, Umutoni             | +250 793 330 328, +250 783 829 899, 26456  | Team 4 | Courses, enrollments, timetable                           |
|14-16 | Deborah, Valentin, Mizero                | +250 791 319 715, +250 793 037 644, 28333  | Team 5 | ML/AI evaluation module, assessments                      |
|17-19 | Gatete, Mushirarungu, Maggy              |                         27380, 28450       | Team 6 | PR's Reviewers / tester                                    |
|20-21 | Ghislaine, Patience                      |                         27380, 27388       | Team 7 | PPT Designers                                             |
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

**Branch:** `feature/auth-team1`

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

**Branch:** `feature/models-team2`

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

All models defined, migrations applied, admin interface functional with sample data.

------------------------------------------------------------------------

## 🔹 Team 3: (+254 790 877089~Anduru/+250 782 802 631~Praise Mutijima) -- Frontend & Dashboard

**Branch:** `feature/frontend-team3`

### Tasks:

-   Create base.html template with blocks (title, content, extra_css, extra_js)
-   Refactor all existing templates (login.html, signup.html, forgot_password.html, dashboard.html) to extend base.html
-   Move inline styles to external CSS files (e.g., css/dashboard.css, css/auth.css)
-   Make dashboard dynamic: replace static sample data with real data from context (passed from views)
-   Improve mobile responsiveness for all pages
-   Add JavaScript enhancements (form validation, AJAX for smoother UX where needed)

### Methodology:

-   Base Template: Design a consistent layout with navbar and footer. Use {% block content %} for page-specific content.
-   CSS Organization: Create static/css/main.css for global styles; separate files for specific pages if needed. Use CSS variables for theming.
-   Dashboard Dynamic: Work with backend members to ensure views pass correct context (e.g., enrolled_courses, timetable, announcements). Use Django template tags to loop and display data.
-   Responsive Testing: Use browser dev tools to test on various screen sizes; adjust media queries.
-   JavaScript: Implement client-side form validation for signup/login. Add loading spinners for async operations (like file upload).
- Accessibility: Ensure proper ARIA labels and semantic HTML.

### Deliverable PR:

Refactored templates with clean, responsive design; dashboard shows real data; no inline styles.

------------------------------------------------------------------------

## 🔹 Team 4: (+250 793 330 328 ~Josiane🤍/Diane Auca +250 783 829 899) -- Courses & Timetable

**Branch:** `feature/courses-team4`

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

Functional course browsing, enrollment, and timetable display.

------------------------------------------------------------------------

## 🔹 Team 5: (Deborah +250 791 319 715 / Valentin +250 793 037 644
  ) -- Assessments & ML

**Branch:** `feature/ml-team5`

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

## 🔹 Team 6: (Gatete, Mushirarungu, Maggy) -- PR Reviewers / Testers

**Branch:** N/A (works across all feature branches)

### Responsibilities:

-   Review pull requests for code quality, functionality, and adherence to project standards.
-   Test new features manually and report any bugs or issues.
-   Ensure documentation (README, TASKS.md) is updated with changes.
-   Collaborate with developers to resolve issues found during testing.

### Methodology:

-   Use GitHub PR interface for code reviews, providing constructive feedback and suggestions.
-   Pull and test feature branches locally to verify functionality.
-   Document test cases and results.
-   Communicate findings via WhatsApp group or PR comments.

### Deliverable:

Quality assurance reports and approved PRs; updated documentation if needed.

------------------------------------------------------------------------

## 🔹 Team 7: (Ghislaine, Patience) -- PPT Designers

**Branch:** `feature/ppt-team7`

### Responsibilities:

-   Create PowerPoint presentations for project updates, demos, and documentation.
-   Design slides for project showcases.
-   Gather content from team leads and incorporate it into visually appealing slides.

### Methodology:

-   Use PowerPoint or Google Slides for creating presentations.
-   Coordinate with team members to collect necessary content, screenshots, and data.
-   Ensure presentations are professional, consistent with project branding, and easy to understand.
-   Test presentations for clarity and flow.

### Deliverable PR:

PPT files committed to the repository or shared via our WhatsApp group; updated with latest project information.

------------------------------------------------------------------------

# Additional Tasks

  Task                    Suggested Assignee
  ----------------------- --------------------
  Finance module          Team 4
  Announcements system    Team 3
  Transcript generation   Team 2
  API (DRF)               Team 2
  Testing                 Team 6(same time this task is for we all)

------------------------------------------------------------------------

# Timeline (Everyday work on this Project like iff the deadline is tomorrow)

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
