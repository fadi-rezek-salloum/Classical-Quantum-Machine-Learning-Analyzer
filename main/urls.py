from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dataset-list/', views.DataSetList.as_view(), name='dataset_list'),
    path('dataset-detail/<pk>/', views.DataSetDetail.as_view(), name='dataset_details'),

    path('advanced', views.advanced, name='advanced'),
]