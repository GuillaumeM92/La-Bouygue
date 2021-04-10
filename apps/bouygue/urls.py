from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.landing, name='bouygue-landing'),
    path('home/', views.home, name='bouygue-home'),
]
