from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from apps.agenda.models import Exchange, Reservation
from apps.activities.models import Activity
from apps.info.models import InfoPost
from apps.work.models import Work
from apps.users.models import MyUser
from . import album
from .forms import AnnouncementForm
from .models import Announcement
from .utils import safe_next
import random


def landing(request):
    try:
        if request.user.is_authenticated:
            return HttpResponseRedirect('home')
        else:
            return render(request, 'bouygue/landing.html')
    except NotImplementedError:
        return render(request, 'bouygue/landing.html')


@login_required
def home(request):
    user = request.user
    today = timezone.localdate()
    # Administrators see pending registrations here, even if the notice e-mail was lost
    pending_accounts = 0
    if user.is_staff or user.is_superuser:
        pending_accounts = MyUser.objects.filter(is_active=False, last_login__isnull=True).count()
    stays = Reservation.objects.filter(end_date__gte=today).select_related('user').order_by('start_date', 'end_date')
    photos = album.all_photos()
    return render(request, 'bouygue/home.html', {
        'title': 'Accueil',
        'reservations_length': Reservation.objects.count() - user.reservations_viewed,
        'activities_length': Activity.objects.count() - user.activities_viewed,
        'infoposts_length': InfoPost.objects.count() - user.informations_viewed,
        'works_length': Work.objects.count() - user.works_viewed,
        'users_length': MyUser.objects.filter(is_active=True).count() - user.users_viewed,
        'pending_accounts': pending_accounts,
        'exchanges_waiting': Exchange.objects.pending().filter(requested__user=user).count(),
        'announcements': Announcement.objects.current().select_related('author'),
        'stays_now': [stay for stay in stays if stay.start_date <= today],
        'stays_next': [stay for stay in stays if stay.start_date > today][:4],
        'slideshow': random.sample(photos, min(5, len(photos))),
        'photo_count': len(photos),
    })


@login_required
def photo_album(request):
    page = Paginator(album.all_photos(), 24).get_page(request.GET.get('page'))
    return render(request, 'bouygue/album.html', {
        'title': 'Album photos',
        'page_obj': page,
        'paginator': page.paginator,
        'is_paginated': page.has_other_pages(),
    })


def _check_admin(user):
    if not (user.is_staff or user.is_superuser):
        raise PermissionDenied


@login_required
def announcements(request):
    """Administrators publish announcements and take them down."""
    _check_admin(request.user)
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(author=request.user)
        messages.success(request, "Annonce publiée : chaque membre la verra à sa prochaine visite.")
        return redirect('announcements')
    return render(request, 'bouygue/announcements.html', {
        'title': 'Annonces',
        'form': form,
        'current': Announcement.objects.current().select_related('author'),
        'past': Announcement.objects.filter(expires_at__lte=timezone.now()).select_related('author')[:10],
    })


@login_required
@require_POST
def announcement_end(request, pk):
    _check_admin(request.user)
    announcement = get_object_or_404(Announcement.objects.current(), pk=pk)
    announcement.expires_at = timezone.now()
    announcement.save()
    messages.success(request, "Annonce retirée.")
    return redirect('announcements')


@login_required
@require_POST
def announcements_read(request):
    """The member closes the pop-up with "J'ai lu": it stops showing up."""
    ids = request.POST.getlist('announcement')
    for announcement in Announcement.objects.current().filter(pk__in=ids):
        announcement.read_by.add(request.user)
    return redirect(safe_next(request, 'bouygue-home'))


def data_policy(request):
    return render(request, 'bouygue/data-policy.html')


# Custom error pages
def bad_request(request, exception):
    return render(request, 'errors/error-400.html', status=400)


def permission_denied(request, exception):
    return render(request, 'errors/error-403.html', status=403)


def page_not_found(request, exception):
    return render(request, 'errors/error-404.html', status=404)


def server_error(request):
    return render(request, 'errors/error-500.html', status=500)
