# habits/forms.py
from django import forms
from .models import Habit

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'category', 'frequency', 'start_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Drink 2L of water'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
