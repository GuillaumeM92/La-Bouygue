from django.shortcuts import render
from django.http import HttpResponseRedirect
from apps.users.models import MyUser
from apps.blog.models import Post
from apps.info.models import InfoPost


def landing(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    else:
        return render(request, 'bouygue/landing.html')


def home(request):
    user = request.user
    posts_length = len(Post.objects.all()) - user.discussions_read
    infoposts_length = len(InfoPost.objects.all()) - user.informations_read
    return render(request, 'bouygue/home.html', {'title': 'Home', 'posts_length': posts_length, 'infoposts_length': infoposts_length})

from django.urls import path

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('sentry-debug/', trigger_error),
    # ...
]
