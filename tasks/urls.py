# tasks/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskList.as_view(), name='list'),
    path('create/', views.TaskCreate.as_view(), name='create'),
    path('edit/<int:pk>/', views.TaskUpdate.as_view(), name='edit'), # For full edit
    path('toggle/<int:pk>/', views.TaskToggleComplete.as_view(), name='toggle_complete'), # For simple button
]

