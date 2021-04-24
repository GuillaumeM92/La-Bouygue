from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from apps.agenda.models import Reservation
from apps.blog.models import Post
from apps.activities.models import Activity
from apps.info.models import InfoPost
from apps.work.models import Work


def landing(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    else:
        return render(request, 'bouygue/landing.html')


@login_required
def home(request):
    user = request.user
    reservations_length = len(Reservation.objects.all()) - user.reservations_viewed
    posts_length = len(Post.objects.all()) - user.discussions_viewed
    activities_length = len(Activity.objects.all()) - user.activities_viewed
    infoposts_length = len(InfoPost.objects.all()) - user.informations_viewed
    works_length = len(Work.objects.all()) - user.works_viewed
    response = render(request, 'bouygue/home.html', {
        'title': 'Accueil',
        'reservations_length': reservations_length,
        'posts_length': posts_length,
        'activities_length': activities_length,
        'infoposts_length': infoposts_length,
        'works_length': works_length
    })
    return response


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
