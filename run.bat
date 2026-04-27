@echo off
set DJANGO_SETTINGS_MODULE=auca_project_mimic.settings.development

echo Running migrations...
py manage.py migrate

echo.
echo ============================================
echo   Server starting at http://127.0.0.1:8000/
echo   Login: student@auca.ac.rw / student123
echo   Login: staff@auca.ac.rw   / staff123
echo   Press CTRL+C to stop
echo ============================================
echo.

py manage.py runserver
