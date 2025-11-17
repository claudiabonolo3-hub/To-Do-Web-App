from django.db import models
 
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True) # For calendar/reminders later
 
    def __str__(self):
        return self.title
 
    class Meta:
        # Order the tasks by completion status (incomplete first)
        # and then by due date
        ordering = ['complete', 'due_date']