# tasks/views.py
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Task
 
class TaskList(ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'tasks/task_list.html'
 
class TaskCreate(CreateView):
    model = Task
    fields = ['title', 'description', 'due_date']
    success_url = reverse_lazy('list')
    template_name = 'tasks/task_form.html' # Create this next!