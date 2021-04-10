from django.urls import path
from . import views
from .views import ActivitiesListView

urlpatterns = [
    path('activities/', ActivitiesListView.as_view(), name='activities'),
    path('activity/<int:pk>/', views.activity_detail, name='activity-detail'),
]
