# todo_project/todo_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Direct all root traffic to the 'todo_app' URLs
    path('', include('todo_app.urls')), 
]