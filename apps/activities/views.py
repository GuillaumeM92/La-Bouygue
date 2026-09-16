from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from apps.bouygue import posts
from .models import Activity, ActivityComment

FIELDS = ["title", "image", "content", "image2", "content2", "difficulty", "duration", "distance"]
IMAGES = {"image_fields": ("image", "image2"), "image_labels": {"image2": "Deuxième image"}}


class ActivityListView(posts.CountsVisit, LoginRequiredMixin, ListView):
    model = Activity
    seen_field = "activities_viewed"
    template_name = "activities/activities.html"
    context_object_name = "activities"
    ordering = ["-date_posted"]
    paginate_by = 7


@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    context, posted = posts.comment_thread(request, activity.activitycomment_set.all(),
                                           posts.comment_form(ActivityComment), activity, activity=activity)
    if posted:
        return redirect("activity-detail", pk=pk)
    return render(request, "activities/activity-detail.html",
                  dict(context, title="Activité", activity=activity))


class ActivityCreateView(posts.PostCreateView):
    model = Activity
    template_name = "activities/activity-create.html"
    fields = FIELDS
    image_fields = IMAGES["image_fields"]
    image_labels = IMAGES["image_labels"]


class ActivityUpdateView(posts.PostUpdateView):
    model = Activity
    template_name = "activities/activity-update.html"
    fields = FIELDS
    image_fields = IMAGES["image_fields"]
    image_labels = IMAGES["image_labels"]
    success_message = "L'activité a été modifiée."


class ActivityDeleteView(posts.PostDeleteView):
    model = Activity
    template_name = "activities/activity-delete.html"
    context_object_name = "activity"
    list_url = "/activities/"
    success_message = "L'activité a été supprimée."


class ActivityCommentUpdateView(posts.CommentUpdateView):
    model = ActivityComment


class ActivityCommentDeleteView(posts.CommentDeleteView):
    model = ActivityComment
    list_url = "/activities/"
