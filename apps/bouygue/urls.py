from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.landing, name='bouygue-landing'),
    path('home/', views.home, name='bouygue-home'),
    path('sentry-debug/', views.trigger_error, name='sentry-debug')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
