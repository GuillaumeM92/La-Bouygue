from . import views
from django.urls import path
from .views import InfoPostListView, InfoPostCreateView, InfoPostUpdateView, InfoPostDeleteView, UserInfoPostListView, InfoCommentUpdateView, InfoCommentDeleteView

urlpatterns = [
    path('info/', InfoPostListView.as_view(), name='info'),
    path('info/user/<str:surname>/<str:name>', UserInfoPostListView.as_view(), name='user-infoposts'),
    path('info/<int:pk>/', views.infopost_detail, name='infopost-detail'),
    path('info/new/', InfoPostCreateView.as_view(), name='infopost-create'),
    path('info/<int:pk>/update/', InfoPostUpdateView.as_view(), name='infopost-update'),
    path('info/<int:pk>/delete/', InfoPostDeleteView.as_view(), name='infopost-delete'),
    path('info/comment/<int:pk>/update/', InfoCommentUpdateView.as_view(), name='infocomment-update'),
    path('info/comment/<int:pk>/delete/', InfoCommentDeleteView.as_view(), name='infocomment-delete'),
]

# path('user/<str:surname>/<str:name>', UserPostListView.as_view(), name='user-posts'),
# path('blog/<int:pk>/', views.post_detail, name='post-detail'),
# path('blog/new/', PostCreateView.as_view(), name='post-create'),
# path('blog/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
# path('blog/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
# path('blog/comment/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),
# path('blog/comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
