"""Exchange requests: a member offers one of their stays for someone else's dates."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.views.decorators.http import require_POST

from apps.users.emails import send_quietly
from .models import Exchange, Reservation


def _dates(start, end):
    if start == end:
        return "le " + date_format(start, "j F Y")
    return "du {} au {}".format(date_format(start, "j F"), date_format(end, "j F Y"))


def _person(user):
    return f"{user.surname} {user.name}".strip() or user.email


def _page_link(request):
    return request.build_absolute_uri(reverse("exchanges"))


@login_required
@require_POST
def exchange_request(request):
    user = request.user
    today = timezone.localdate()
    requested_id, offered_id = request.POST.get("requested", ""), request.POST.get("offered", "")
    requested = Reservation.objects.filter(pk=requested_id, end_date__gte=today).exclude(user=user).first() \
        if requested_id.isdigit() else None
    offered = Reservation.objects.filter(pk=offered_id, user=user, end_date__gte=today).first() \
        if offered_id.isdigit() else None
    if requested is None or offered is None:
        messages.error(request, "Cet échange n'est pas possible : l'un des deux séjours n'existe plus ou est passé.")
        return redirect("agenda")
    if Exchange.objects.pending().filter(offered=offered, requested=requested).exists():
        messages.info(request, "Vous avez déjà demandé cet échange : la réponse est attendue.")
        return redirect("exchanges")

    exchange = Exchange.objects.create(
        requester=user, offered=offered, requested=requested,
        message=request.POST.get("message", "").strip()[:2000],
        offered_start=offered.start_date, offered_end=offered.end_date,
        requested_start=requested.start_date, requested_end=requested.end_date)
    body = (
        f"Bonjour,\n\n{_person(user)} vous propose d'échanger vos dates sur le calendrier de La Bouygue :\n\n"
        f"- votre séjour « {requested.name} », {_dates(requested.start_date, requested.end_date)}\n"
        f"- contre son séjour « {offered.name} », {_dates(offered.start_date, offered.end_date)}\n\n"
        + (f"Son message : {exchange.message}\n\n" if exchange.message else "")
        + f"Pour accepter ou refuser : {_page_link(request)}\n"
    )
    send_quietly("La Bouygue - Demande d'échange de séjour", body, requested.user.email)
    messages.success(request, f"Demande envoyée à {_person(requested.user)}. Vous serez prévenu de sa réponse par e-mail.")
    return redirect("exchanges")


@login_required
def exchanges(request):
    user = request.user
    mine = Exchange.objects.select_related("requester", "offered__user", "requested__user")
    return render(request, "agenda/exchanges.html", {
        "title": "Échanges de séjours",
        "received": mine.pending().filter(requested__user=user),
        "sent": mine.pending().filter(requester=user),
        "history": mine.exclude(status=Exchange.PENDING)
                       .filter(Q(requester=user) | Q(requested__user=user) | Q(offered__user=user))[:15],
    })


@login_required
@require_POST
def exchange_answer(request, pk):
    accept = request.POST.get("answer") == "accept"
    with transaction.atomic():
        exchange = get_object_or_404(
            Exchange.objects.select_for_update().select_related("offered", "requested", "requester"),
            pk=pk, status=Exchange.PENDING, requested__user=request.user)
        exchange.answered_at = timezone.now()
        requester = exchange.requester
        if accept and not exchange.still_valid():
            exchange.status = Exchange.OUTDATED
            exchange.save()
            messages.error(request, "L'un des deux séjours a changé depuis la demande : l'échange n'est plus possible. "
                                    "Il faudra en refaire une.")
            return redirect("exchanges")
        if accept:
            exchange.swap()
            exchange.status = Exchange.ACCEPTED
            exchange.save()
            # Other requests about these two stays refer to dates that no longer hold
            (Exchange.objects.pending()
             .filter(Q(offered__in=[exchange.offered, exchange.requested])
                     | Q(requested__in=[exchange.offered, exchange.requested]))
             .update(status=Exchange.OUTDATED, answered_at=exchange.answered_at))
        else:
            exchange.status = Exchange.DECLINED
            exchange.save()

    if accept:
        body = (f"Bonjour,\n\n{_person(request.user)} a accepté l'échange : votre séjour « {exchange.offered.name} » "
                f"est désormais {_dates(exchange.offered.start_date, exchange.offered.end_date)}, et le sien "
                f"{_dates(exchange.requested.start_date, exchange.requested.end_date)}.\n\n"
                f"Le calendrier est à jour : {request.build_absolute_uri(reverse('agenda'))}\n")
        send_quietly("La Bouygue - Échange de séjour accepté", body, requester.email)
        messages.success(request, "Échange accepté : les dates des deux séjours ont été échangées.")
    else:
        body = (f"Bonjour,\n\n{_person(request.user)} n'a pas accepté l'échange de votre séjour "
                f"« {exchange.offered.name} » contre « {exchange.requested.name} ». "
                "Vos dates restent inchangées.\n")
        send_quietly("La Bouygue - Échange de séjour refusé", body, requester.email)
        messages.success(request, "Demande refusée. La personne en est informée.")
    return redirect("exchanges")


@login_required
@require_POST
def exchange_cancel(request, pk):
    exchange = get_object_or_404(Exchange, pk=pk, status=Exchange.PENDING, requester=request.user)
    exchange.status = Exchange.CANCELLED
    exchange.answered_at = timezone.now()
    exchange.save()
    messages.success(request, "Demande d'échange annulée.")
    return redirect("exchanges")
