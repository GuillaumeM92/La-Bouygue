from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from apps.agenda.models import Reservation
from apps.blog.models import Post, Comment
from apps.activities.models import Activity
from apps.info.models import InfoPost
from apps.work.models import Work
import random


def landing(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    else:
        return render(request, 'bouygue/landing.html')


def get_random_image(queryset):
    rand_int = random.randint(0, queryset.count() - 1)
    return queryset[rand_int].image


@login_required
def home(request):
    user = request.user
    reservations_length = len(Reservation.objects.all()) - user.reservations_viewed
    posts_length = len(Post.objects.all()) - user.discussions_viewed
    activities_length = len(Activity.objects.all()) - user.activities_viewed
    infoposts_length = len(InfoPost.objects.all()) - user.informations_viewed
    works_length = len(Work.objects.all()) - user.works_viewed
    # get posts and comments that contain images
    posts_with_images = Post.objects.exclude(image='')
    comments_with_images = Comment.objects.exclude(image='')
    # get 5 random images for the caroussel (and make sure not to pick the same one twice)
    caroussel_img_1 = get_random_image(posts_with_images)
    caroussel_img_2 = get_random_image(comments_with_images)
    caroussel_img_3 = get_random_image(posts_with_images.exclude(image=caroussel_img_1))
    caroussel_img_4 = get_random_image(comments_with_images.exclude(image=caroussel_img_2))
    caroussel_img_5 = get_random_image(comments_with_images.exclude(image=caroussel_img_2).exclude(image=caroussel_img_4))
    
    response = render(request, 'bouygue/home.html', {
        'title': 'Accueil',
        'reservations_length': reservations_length,
        'posts_length': posts_length,
        'activities_length': activities_length,
        'infoposts_length': infoposts_length,
        'works_length': works_length,
        'caroussel_img_1': caroussel_img_1,
        'caroussel_img_2': caroussel_img_2,
        'caroussel_img_3': caroussel_img_3,
        'caroussel_img_4': caroussel_img_4,
        'caroussel_img_5': caroussel_img_5
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
