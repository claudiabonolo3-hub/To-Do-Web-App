from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Task


class TaskList(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'


class TaskCreate(CreateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('task_list')
