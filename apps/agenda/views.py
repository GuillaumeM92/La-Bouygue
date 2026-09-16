import json
from django.db.models import F
from django.shortcuts import render, redirect
from django.utils.formats import date_format
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Reservation
from .forms import ReservationForm


def _stay_dates(stay):
    if stay.start_date == stay.end_date:
        return "le " + date_format(stay.start_date, "j F")
    return "du {} au {}".format(date_format(stay.start_date, "j F"), date_format(stay.end_date, "j F"))


def _warn_about_overlaps(request, stay):
    others = Reservation.objects.overlapping(stay)
    if others:
        listed = " ; ".join(f"{other.name} ({_stay_dates(other)})" for other in others)
        messages.warning(request, "Ce séjour tombe en même temps que : " + listed
                         + ". Pensez à vous coordonner.")


@login_required
def show_agenda(request):
    user = request.user
    # On a refused form, the page opens the stay window again with the errors
    reopen = None
    if request.method == "POST":
        stay_id = request.POST.get("id", "")
        instance = None
        if stay_id:
            instance = Reservation.objects.filter(pk=stay_id).first() if stay_id.isdigit() else None
            if instance is None:
                messages.error(request, "Ce séjour n'existe plus.")
                return redirect("agenda")
            if not instance.can_be_changed_by(user):
                messages.error(request, "Ce séjour ne vous appartient pas : vous ne pouvez pas le modifier.")
                return redirect("agenda")
        form = ReservationForm(request.POST, instance=instance)
        if form.is_valid():
            stay = form.save(commit=False)
            if instance is None:
                stay.user = user
            stay.save()
            messages.success(request, "Le séjour a été modifié." if instance else "Votre séjour a été ajouté au calendrier.")
            _warn_about_overlaps(request, stay)
            return redirect("agenda")
        reopen = stay_id or "new"
    else:
        form = ReservationForm(initial={"name": f"{user.surname} {user.name}".strip()})
    user.reservations_viewed = Reservation.objects.count()
    user.save()
    return render(request, "agenda/agenda.html", {
        "title": "Calendrier",
        "form": form,
        "calendar_config": {
            "userId": user.id,
            "isAdmin": user.is_staff or user.is_superuser,
            "defaultName": f"{user.surname} {user.name}".strip(),
            "reopen": reopen,
        },
    })


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
    messages.success(request, "Le séjour a été supprimé.")
    return JsonResponse({'deleted': stay.name})


@login_required
def reservations(request):
    """Every stay, with its owner's name, for the calendar script."""
    data = list(Reservation.objects.order_by("start_date").values(
        "id", "name", "description", "start_date", "end_date", "user_id",
        owner_surname=F("user__surname"), owner_name=F("user__name")))
    return JsonResponse(data, safe=False)
