# todo_app/urls.py - COMPLETE UPDATED VERSION

from django.urls import path
from . import views

urlpatterns = [
    # Landing & Auth
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Onboarding Flow
    path('onboarding/welcome/', views.onboarding_welcome, name='onboarding_welcome'),
    path('onboarding/preference/', views.onboarding_preference, name='onboarding_preference'),
    path('onboarding/habits/', views.onboarding_habits, name='onboarding_habits'),
    
    # Main App Views (matching sidebar navigation)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('habits/', views.habits_view, name='habits_view'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('settings/', views.settings_view, name='settings_view'),
    
    # Task CRUD
    path('task/add/', views.add_task, name='add_task'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
     path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
     
    # Habit CRUD
    path('habit/add/', views.add_habit, name='add_habit'),
    path('habit/<int:habit_id>/complete/', views.complete_habit, name='complete_habit'),
    path('habit/<int:habit_id>/delete/', views.delete_habit, name='delete_habit'),
    
    # AJAX Endpoints
    path('api/theme/update/', views.update_theme_ajax, name='update_theme_ajax'),
]