import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core import serializers

from .models import Reservation
from .forms import ReservationForm

def show_agenda(request):
    if request.method == "POST":
        user = request.user
        form = ReservationForm(request.POST)
        # get the reservation id, if it does not exist, set it to 0
        id = request.POST.get('id', 0)

        if form.is_valid():
            try:
                Reservation.objects.create_or_update_reservation(form, user, id)
                if id == 0:
                    messages.success(request, str("Votre réservation a été créée avec succès !"))
                else:
                    messages.success(request, str("Votre réservation a été modifiée avec succès !"))
            except (IndexError, ValidationError):
                messages.error(request, str("LE FORMAT DE LA DATE EST INVALIDE ! MERCI DE RÉESSAYER."))

        else:
            messages.error(request, str('ERREUR : ' + form.cleaned_data["error_message"]))
            form = ReservationForm(request.POST)

    else:
        user = request.user
        form = ReservationForm()
    return render(request, 'agenda/agenda.html', {'title': 'Calendrier', "form": form})

def get_reservation_details(request):
    """This view is used when the user clicks on an existing reservation"""
    mydata = json.loads(request.body)
    reservation_id = mydata['id']
    reservation = Reservation.objects.filter(id=reservation_id)
    return JsonResponse(serializers.serialize('json', reservation), safe=False)

def delete_reservation(request):
    """This view is used to delete a user reservation"""
    mydata = json.loads(request.body)
    reservation_id = mydata['id']
    reservation = Reservation.objects.filter(id=reservation_id)
    reservation.delete()
    messages.success(request, str("Votre réservation a bien été supprimée !"))
    return JsonResponse(serializers.serialize('json', reservation), safe=False)

def reservations(request):
    data = list(Reservation.objects.all().values())  # wrap in list(), because QuerySet is not JSON serializable
    return JsonResponse(data, safe=False)
