from django.contrib import admin
from django.urls import path, include

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
