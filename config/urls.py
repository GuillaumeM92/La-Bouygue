from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.templatetags.static import static as static_url
from django.urls import path, include
from django.utils.functional import lazy
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Browsers and feed readers ask for /favicon.ico whatever the page says
    path('favicon.ico', RedirectView.as_view(
        url=lazy(static_url, str)('bouygue/assets/img/favicon.ico'))),
    path('', include('apps.bouygue.urls')),
    path('', include('apps.users.urls')),
    path('', include('apps.agenda.urls')),
    path('', include('apps.activities.urls')),
    path('', include('apps.info.urls')),
    path('', include('apps.work.urls')),
]

# Uploaded images, in development only: in production Nginx serves /media/
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'apps.bouygue.views.bad_request'
handler403 = 'apps.bouygue.views.permission_denied'
handler404 = 'apps.bouygue.views.page_not_found'
handler500 = 'apps.bouygue.views.server_error'
