# tasks/admin.py
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'complete', 'due_date', 'created')
    list_filter = ('complete',)
    search_fields = ('title', 'description')
