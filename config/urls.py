from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.bouygue.urls')),
    path('', include('apps.users.urls')),
    path('', include('apps.agenda.urls')),
    path('', include('apps.blog.urls')),
    path('', include('apps.activities.urls')),
    path('', include('apps.info.urls')),
    path('', include('apps.work.urls')),
    path('', include('apps.budget.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
