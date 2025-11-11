# tasks/urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('', views.TaskList.as_view(), name='list'),
    path('create/', views.TaskCreate.as_view(), name='create'),
    # You'll add update and delete here later
]