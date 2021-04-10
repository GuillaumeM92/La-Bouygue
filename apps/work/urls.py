from . import views
from django.urls import path
# from .views import WorkListView
# InfoPostCreateView, InfoPostUpdateView, InfoPostDeleteView, UserInfoPostListView

urlpatterns = [
    path('work/', views.work, name='work'),
    path('works/', views.works, name='works'),
    # path('info/user/<str:surname>/<str:name>', UserInfoPostListView.as_view(), name='user-infoposts'),
    # path('info/<int:pk>/', views.infopost_detail, name='infopost-detail'),
    # path('info/new/', InfoPostCreateView.as_view(), name='infopost-create'),
    # path('info/<int:pk>/update/', InfoPostUpdateView.as_view(), name='infopost-update'),
    # path('info/<int:pk>/delete/', InfoPostDeleteView.as_view(), name='infopost-delete'),
]
