from django.urls import path
from . import views
from .views import ActivityListView, ActivityCreateView, ActivityUpdateView, ActivityDeleteView, UserActivityListView, ActivityCommentUpdateView, ActivityCommentDeleteView

urlpatterns = [
    path('activities/', ActivityListView.as_view(), name='activities'),
    path('activities/user/<str:surname>/<str:name>', UserActivityListView.as_view(), name='user-activities'),
    path('activities/new/', ActivityCreateView.as_view(), name='activity-create'),
    path('activity/<int:pk>/', views.activity_detail, name='activity-detail'),
    path('activities/<int:pk>/update/', ActivityUpdateView.as_view(), name='activity-update'),
    path('activities/<int:pk>/delete/', ActivityDeleteView.as_view(), name='activity-delete'),
    path('activities/comment/<int:pk>/update/', ActivityCommentUpdateView.as_view(), name='activitycomment-update'),
    path('activities/comment/<int:pk>/delete/', ActivityCommentDeleteView.as_view(), name='activitycomment-delete'),
]
