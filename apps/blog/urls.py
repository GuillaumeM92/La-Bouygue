from . import views
from django.urls import path
from .views import (PostListView, PostCreateView, PostUpdateView, PostDeleteView,
                    CommentUpdateView, CommentDeleteView, UserPostListView)

urlpatterns = [
    path('blog/', PostListView.as_view(), name='blog'),
    path('user/<str:surname>/<str:name>', UserPostListView.as_view(), name='user-posts'),
    path('blog/<int:pk>/', views.post_detail, name='post-detail'),
    path('blog/new/', PostCreateView.as_view(), name='post-create'),
    path('blog/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('blog/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('blog/comment/<int:pk>/update/',
         CommentUpdateView.as_view(), name='comment-update'),
    path('blog/comment/<int:pk>/delete/',
         CommentDeleteView.as_view(), name='comment-delete'),
]
