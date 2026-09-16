from django.urls import path
from . import views

urlpatterns = [
    path('agenda/', views.show_agenda, name='agenda'),
    path('reservations/', views.reservations, name='reservations'),
    path('delete_reservation/', views.delete_reservation, name='delete-reservation'),
]
