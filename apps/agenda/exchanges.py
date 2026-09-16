"""Exchange requests: a member offers one of their stays for someone else's dates."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
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


# The e-mails, as (subject, body)

def request_email(requester, offered, requested, message, link):
    return "La Bouygue - Demande d'échange de séjour", (
        f"Bonjour,\n\n{_person(requester)} vous propose d'échanger vos dates sur le calendrier de La Bouygue :\n\n"
        f"- votre séjour « {requested.name} », {_dates(requested.start_date, requested.end_date)}\n"
        f"- contre son séjour « {offered.name} », {_dates(offered.start_date, offered.end_date)}\n\n"
        + (f"Son message : {message}\n\n" if message else "")
        + f"Pour accepter ou refuser : {link}\n")


def answer_email(accepted, answerer, offered, requested, link):
    """To the requester; `offered` is their stay, already moved when accepted."""
    if accepted:
        return "La Bouygue - Échange de séjour accepté", (
            f"Bonjour,\n\n{_person(answerer)} a accepté l'échange : votre séjour « {offered.name} » "
            f"est désormais {_dates(offered.start_date, offered.end_date)}, et le sien "
            f"{_dates(requested.start_date, requested.end_date)}.\n\nLe calendrier est à jour : {link}\n")
    return "La Bouygue - Échange de séjour refusé", (
        f"Bonjour,\n\n{_person(answerer)} n'a pas accepté l'échange de votre séjour « {offered.name} » "
        f"contre « {requested.name} ». Vos dates restent inchangées.\n")


def contact_email(sender, stay, text):
    return f"La Bouygue - Message de {_person(sender)} au sujet de votre séjour", (
        f"Bonjour,\n\n{_person(sender)} vous écrit au sujet de votre séjour « {stay.name} », "
        f"{_dates(stay.start_date, stay.end_date)} :\n\n{text}\n\n"
        f"Pour lui répondre, répondez simplement à cet e-mail ({sender.email}).\n")


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
    send_quietly(*request_email(user, offered, requested, exchange.message, _page_link(request)),
                 requested.user.email)
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

    send_quietly(*answer_email(accept, request.user, exchange.offered, exchange.requested,
                               request.build_absolute_uri(reverse("agenda"))), requester.email)
    if accept:
        messages.success(request, "Échange accepté : les dates des deux séjours ont été échangées.")
    else:
        messages.success(request, "Demande refusée. La personne en est informée.")
    return redirect("exchanges")


CONTACTS_PER_HOUR = 5


@login_required
@require_POST
def contact_owner(request, pk):
    """A member writes to whoever posed a stay; the owner answers by replying to the e-mail."""
    user = request.user
    stay = get_object_or_404(Reservation.objects.select_related("user"), pk=pk)
    text = request.POST.get("message", "").strip()[:2000]
    if stay.user_id == user.id or not text:
        messages.error(request, "Le message est vide." if text == "" else "C'est votre propre séjour.")
        return redirect("agenda")
    key = f"agenda.contact.{user.id}"
    sent = cache.get(key, 0)
    if sent >= CONTACTS_PER_HOUR:
        messages.error(request, "Vous avez déjà envoyé plusieurs messages cette heure-ci : réessayez un peu plus tard.")
        return redirect("agenda")
    cache.set(key, sent + 1, 60 * 60)
    if send_quietly(*contact_email(user, stay, text), stay.user.email, reply_to=user.email):
        messages.success(request, f"Message envoyé à {_person(stay.user)}. Sa réponse arrivera dans votre boîte e-mail.")
    else:
        messages.error(request, "Le message n'a pas pu partir. Réessayez plus tard, ou utilisez le carnet d'adresses.")
    return redirect("agenda")


@login_required
@require_POST
def exchange_cancel(request, pk):
    exchange = get_object_or_404(Exchange, pk=pk, status=Exchange.PENDING, requester=request.user)
    exchange.status = Exchange.CANCELLED
    exchange.answered_at = timezone.now()
    exchange.save()
    messages.success(request, "Demande d'échange annulée.")
    return redirect("exchanges")
