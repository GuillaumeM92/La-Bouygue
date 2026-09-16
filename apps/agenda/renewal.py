"""Renew a year's stays a year later: the weeks some members take every year."""
from collections import defaultdict
from datetime import date, timedelta

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format

from apps.bouygue.posts import is_admin
from apps.users.emails import send_quietly
from .models import Reservation


def _on(anchor, year):
    try:
        return anchor.replace(year=year)
    except ValueError:  # 29 February
        return date(year, 2, 28)


def one_year_later(day, anchor=None):
    """The same weekday, as close as possible to the anchor's date the next year.

    A family week runs from the same weekday every year, around the same
    date (Christmas, mid-August). The anchor is the date of the first stay
    of the series: measured from it, the dates never drift from year to year.
    """
    anchor = anchor or day
    # The year of the series this stay belongs to: a 31 December stay may
    # have moved to early January
    season = min((day.year - 1, day.year, day.year + 1), key=lambda y: abs((_on(anchor, y) - day).days))
    target = _on(anchor, season + 1)
    return target + timedelta(days=(day.weekday() - target.weekday() + 3) % 7 - 3)


class Proposal:
    def __init__(self, stay):
        self.stay = stay
        self.anchor = stay.anchor_date or stay.start_date
        self.start = one_year_later(stay.start_date, self.anchor)
        self.end = self.start + (stay.end_date - stay.start_date)
        # A copy already posed (same owner and name, around the same dates)
        self.done = Reservation.objects.filter(
            user_id=stay.user_id, name=stay.name,
            start_date__range=(self.start - timedelta(days=10), self.start + timedelta(days=10))).exists()
        probe = Reservation(pk=-1, start_date=self.start, end_date=self.end)
        self.clashes = [] if self.done else Reservation.objects.overlapping(probe)


def _dates(start, end):
    return "du {} au {}".format(date_format(start, "l j F"), date_format(end, "l j F Y"))


@login_required
def renew_year(request):
    if not is_admin(request.user):
        raise PermissionDenied
    this_year = timezone.localdate().year
    years = sorted({d.year for d in Reservation.objects.dates("start_date", "year")}, reverse=True)
    try:
        year = int(request.GET.get("annee") or request.POST.get("annee") or this_year)
    except ValueError:
        year = this_year
    stays = Reservation.objects.filter(start_date__year=year).select_related("user").order_by("start_date")
    proposals = [Proposal(stay) for stay in stays]

    if request.method == "POST":
        chosen = set(request.POST.getlist("stay"))
        created = []
        with transaction.atomic():
            for proposal in proposals:
                if str(proposal.stay.pk) in chosen and not proposal.done:
                    created.append(Reservation.objects.create(
                        name=proposal.stay.name, description=proposal.stay.description,
                        user=proposal.stay.user, start_date=proposal.start, end_date=proposal.end,
                        anchor_date=proposal.anchor))
        if request.POST.get("notify"):
            by_owner = defaultdict(list)
            for stay in created:
                by_owner[stay.user].append(stay)
            link = request.build_absolute_uri(reverse("agenda"))
            for owner, owned in by_owner.items():
                lines = "\n".join(f"- « {s.name} », {_dates(s.start_date, s.end_date)}" for s in owned)
                send_quietly(
                    f"La Bouygue - Vos séjours {year + 1} sont posés",
                    f"Bonjour,\n\nComme chaque année, ces séjours ont été posés pour vous sur le calendrier de "
                    f"La Bouygue :\n\n{lines}\n\nSi vos projets changent, modifiez-les, supprimez-les ou proposez "
                    f"un échange depuis le calendrier : {link}\n",
                    owner.email)
        if created:
            messages.success(request, f"{len(created)} séjour{'s' if len(created) > 1 else ''} posé"
                                      f"{'s' if len(created) > 1 else ''} pour {year + 1}"
                                      + (", propriétaires prévenus par e-mail." if request.POST.get("notify") else "."))
        else:
            messages.info(request, "Aucun séjour à poser : rien n'était coché, ou tout était déjà reconduit.")
        return redirect(f"{reverse('renew-year')}?annee={year}")

    return render(request, "agenda/renewal.html", {
        "title": "Reconduire les séjours",
        "year": year,
        "next_year": year + 1,
        "years": sorted(set(years) | {this_year}, reverse=True),
        "proposals": proposals,
    })
