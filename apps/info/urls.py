from . import views
from django.urls import path
from .views import (InfoPostListView, InfoPostCreateView, InfoPostUpdateView, InfoPostDeleteView,
                    InfoCommentUpdateView, InfoCommentDeleteView, ActivateUsersListView,
                    AllUsersListView)

urlpatterns = [
    path('info/', InfoPostListView.as_view(), name='info'),
    path('info/<int:pk>/', views.infopost_detail, name='infopost-detail'),
    path('info/new/', InfoPostCreateView.as_view(), name='infopost-create'),
    path('info/<int:pk>/update/', InfoPostUpdateView.as_view(), name='infopost-update'),
    path('info/<int:pk>/delete/', InfoPostDeleteView.as_view(), name='infopost-delete'),
    path('info/comment/<int:pk>/update/',
         InfoCommentUpdateView.as_view(), name='infocomment-update'),
    path('info/comment/<int:pk>/delete/',
         InfoCommentDeleteView.as_view(), name='infocomment-delete'),
    path('info/admin/activate/', ActivateUsersListView.as_view(), name='activate-users'),
    path('info/users/all/', AllUsersListView.as_view(), name='all-users'),
]
