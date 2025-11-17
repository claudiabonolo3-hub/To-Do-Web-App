from django.db import models

class Habit(models.Model):
    CATEGORY_CHOICES = [
        ('Health', 'Health'),
        ('Productivity', 'Productivity'),
        ('Learning', 'Learning'),
        ('Mindfulness', 'Mindfulness'),
        ('Fitness', 'Fitness'),
        ('Other', 'Other'),
    ]

    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='Daily')
    start_date = models.DateField(null=True, blank=True)
    completed_today = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']
