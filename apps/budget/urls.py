from . import views
from django.urls import path

urlpatterns = [
    path('budget/', views.budget, name='budget'),
]
