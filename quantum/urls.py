from django.urls import path

from . import views

urlpatterns = [
    path('', views.quantum, name='quantum'),
    path('result/', views.result, name='result'),
]