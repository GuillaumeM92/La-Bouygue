from django.urls import path
from . import exchanges, renewal, views

urlpatterns = [
    path('agenda/', views.show_agenda, name='agenda'),
    path('reservations/', views.reservations, name='reservations'),
    path('delete_reservation/', views.delete_reservation, name='delete-reservation'),
    path('echanges/', exchanges.exchanges, name='exchanges'),
    path('agenda/reconduire/', renewal.renew_year, name='renew-year'),
    path('echanges/demander/', exchanges.exchange_request, name='exchange-request'),
    path('reservation/<int:pk>/ecrire/', exchanges.contact_owner, name='contact-owner'),
    path('echanges/<int:pk>/repondre/', exchanges.exchange_answer, name='exchange-answer'),
    path('echanges/<int:pk>/annuler/', exchanges.exchange_cancel, name='exchange-cancel'),
]
