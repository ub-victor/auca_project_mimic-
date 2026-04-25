import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auca_project_mimic.settings.development')
application = get_wsgi_application()
