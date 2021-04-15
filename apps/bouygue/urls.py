from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='bouygue-landing'),
    path('home/', views.home, name='bouygue-home'),
    path('data-policy/', views.data_policy, name='bouygue-data-policy'),
]
