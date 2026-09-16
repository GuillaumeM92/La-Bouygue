import json
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
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
                result = Reservation.objects.create_or_update_reservation(form, user, id)
                if id == 0:
                    messages.success(request, str(
                        "Votre séjour a été créé avec succès !"))
                elif result is None:
                    messages.error(request, str(
                        "Ce séjour n'existe plus, ou ne vous appartient pas."))
                else:
                    messages.success(request, str(
                        "Le séjour a été modifié avec succès !"))
                form = ReservationForm()
            except (IndexError, ValueError, ValidationError):
                messages.error(request, str(
                    "LE FORMAT DE LA DATE EST INVALIDE ! MERCI DE RÉESSAYER."))

        else:
            messages.error(request, str('ERREUR : ' + form.cleaned_data.get(
                "error_message", "LE FORMULAIRE EST INCOMPLET. MERCI DE RÉESSAYER.")))
            form = ReservationForm(request.POST)

    else:
        form = ReservationForm()
    user.reservations_viewed = len(Reservation.objects.all())
    user.save()
    return render(request, 'agenda/agenda.html', {'title': 'Calendrier', "form": form})


def _requested_reservation(request):
    """The reservation whose id the calendar sent as JSON, or an error response."""
    try:
        reservation = Reservation.objects.filter(id=json.loads(request.body)['id'])
        found = reservation.first()
    except (ValueError, KeyError, TypeError):
        return None, JsonResponse({'error': "Requête invalide."}, status=400)
    if found is None:
        return None, JsonResponse({'error': "Ce séjour n'existe plus."}, status=404)
    return reservation, None


@login_required
@require_POST
def get_reservation_details(request):
    """This view is used when the user clicks on an existing reservation"""
    reservation, error = _requested_reservation(request)
    if error:
        return error
    return JsonResponse(serializers.serialize('json', reservation), safe=False)


@login_required
@require_http_methods(["DELETE"])
def delete_reservation(request):
    """This view is used to delete a user reservation"""
    reservation, error = _requested_reservation(request)
    if error:
        return error
    stay = reservation.first()
    user = request.user
    if not (user == stay.user or user.is_superuser or user.is_staff):
        return JsonResponse({'error': "Ce séjour ne vous appartient pas."}, status=403)
    stay.delete()
    messages.success(request, str("Le séjour a bien été supprimé !"))
    return JsonResponse({'deleted': stay.name})


@login_required
def reservations(request):
    # wrap in list(), because QuerySet is not JSON serializable
    data = list(Reservation.objects.all().values())
    return JsonResponse(data, safe=False)
