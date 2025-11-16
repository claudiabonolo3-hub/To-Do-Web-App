from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskList.as_view(), name='task_list'),
    path('create/', views.TaskCreate.as_view(), name='task_create'),
]
