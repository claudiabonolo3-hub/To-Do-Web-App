from django.urls import path
from . import views

urlpatterns = [
    path('', views.HabitList.as_view(), name='habit_list'),
    path('create/', views.HabitCreate.as_view(), name='habit_create'),
    path('edit/<int:pk>/', views.HabitUpdate.as_view(), name='habit_edit'),
    path('toggle/<int:pk>/', views.HabitToggleComplete.as_view(), name='habit_toggle'),
]
