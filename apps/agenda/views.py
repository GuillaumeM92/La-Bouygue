import json
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core import serializers
from django.contrib.auth.decorators import login_required
from .models import Reservation
from .forms import ReservationForm


@login_required
def show_agenda(request):
    user = request.user
    if request.method == "POST":
        form = ReservationForm(request.POST)
        # get the reservation id, if it does not exist, set it to 0
        id = request.POST.get('id', 0)

        if form.is_valid():
            try:
                Reservation.objects.create_or_update_reservation(form, user, id)
                if id == 0:
                    messages.success(request, str(
                        "Votre séjour a été créé avec succès !"))
                else:
                    messages.success(request, str(
                        "Le séjour a été modifié avec succès !"))
                form = ReservationForm()
            except (IndexError, ValidationError):
                messages.error(request, str(
                    "LE FORMAT DE LA DATE EST INVALIDE ! MERCI DE RÉESSAYER."))

        else:
            messages.error(request, str(
                'ERREUR : ' + form.cleaned_data["error_message"]))
            form = ReservationForm(request.POST)

    else:
        form = ReservationForm()
    user.reservations_viewed = len(Reservation.objects.all())
    user.save()
    return render(request, 'agenda/agenda.html', {'title': 'Calendrier', "form": form})


@login_required
def get_reservation_details(request):
    """This view is used when the user clicks on an existing reservation"""
    mydata = json.loads(request.body)
    reservation_id = mydata['id']
    reservation = Reservation.objects.filter(id=reservation_id)
    return JsonResponse(serializers.serialize('json', reservation), safe=False)


@login_required
def delete_reservation(request):
    """This view is used to delete a user reservation"""
    mydata = json.loads(request.body)
    reservation_id = mydata['id']
    reservation = Reservation.objects.filter(id=reservation_id)
    user = request.user
    if user == reservation.first().user or user.is_superuser or user.is_staff:
        reservation.first().delete()
        messages.success(request, str("Le séjour a bien été supprimé !"))
        return JsonResponse(serializers.serialize('json', reservation), safe=False)


@login_required
def reservations(request):
    # wrap in list(), because QuerySet is not JSON serializable
    data = list(Reservation.objects.all().values())
    return JsonResponse(data, safe=False)
