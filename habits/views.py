# habits/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Habit
from .forms import HabitForm
from django.views import View


# 🌿 Show all habits
class HabitList(ListView):
    model = Habit
    template_name = 'habits/habit_list.html'
    context_object_name = 'habits'


# 🌸 Create a new habit
class HabitCreate(CreateView):
    model = Habit
    form_class = HabitForm
    template_name = 'habits/habit_form.html'
    success_url = reverse_lazy('habit_list')


# ✏️ Update/Edit existing habit
class HabitUpdate(UpdateView):
    model = Habit
    form_class = HabitForm
    template_name = 'habits/habit_form.html'
    success_url = reverse_lazy('habit_list')


# 🌞 Toggle completion (mark habit done / not done)
class HabitToggleComplete(View):
    def post(self, request, pk):
        habit = Habit.objects.get(pk=pk)
        habit.completed_today = not habit.completed_today
        habit.save()
        return redirect('habit_list')
