from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('assessments/', include('apps.assessments.urls')),
    path('courses/', include('apps.courses.urls')),
    path('core/', include('apps.core.urls')),
    path('panel/', include('apps.accounts.admin_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
