from django.urls import path
from . import views
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('agenda/', views.show_agenda, name='agenda'),
    path('reservations/', views.reservations, name='reservations'),
    path('reservation/', views.get_reservation_details, name='view-reservation'),
    path('delete_reservation/', views.delete_reservation, name='delete-reservation'),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
