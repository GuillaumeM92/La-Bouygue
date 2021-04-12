from django.urls import path
from . import views
from .views import WorkListView, WorkCreateView, WorkUpdateView, WorkDeleteView, UserWorkListView, WorkCommentUpdateView, WorkCommentDeleteView

urlpatterns = [
    path("work/", WorkListView.as_view(), name="work"),
    path("work/user/<str:surname>/<str:name>", UserWorkListView.as_view(), name="user-work"),
    path("work/new/", WorkCreateView.as_view(), name="work-create"),
    path("work/<int:pk>/", views.work_detail, name="work-detail"),
    path("work/<int:pk>/update/", WorkUpdateView.as_view(), name="work-update"),
    path("work/<int:pk>/delete/", WorkDeleteView.as_view(), name="work-delete"),
    path('work/comment/<int:pk>/update/', WorkCommentUpdateView.as_view(), name='workcomment-update'),
    path('work/comment/<int:pk>/delete/', WorkCommentDeleteView.as_view(), name='workcomment-delete'),
]
