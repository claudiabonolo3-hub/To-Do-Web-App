# tasks/views.py
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Task
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView # <-- New Import
from django.shortcuts import redirect # <-- New Import
from django.views import View # <-- New Import
 
class TaskList(ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'tasks/task_list.html'
 
class TaskCreate(CreateView):
    model = Task
    fields = ['title', 'description', 'due_date']
    success_url = reverse_lazy('list')
    template_name = 'tasks/task_form.html' # Create this next!

    # --- New: Simple View to toggle 'complete' ---
class TaskToggleComplete(View):
    def post(self, request, pk):
        task = Task.objects.get(pk=pk)
        task.complete = not task.complete
        task.save()
        return redirect('list')
    
# <--- Ensure this class is exactly named TaskUpdate and is present --->
class TaskUpdate(UpdateView):
    model = Task
    fields = ['title', 'description', 'complete', 'due_date']
    success_url = reverse_lazy('list')
    template_name = 'tasks/task_form.html'

