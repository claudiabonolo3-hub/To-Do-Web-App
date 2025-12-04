# todo_project/todo_app/admin.py
from django.contrib import admin
from .models import UserProfile, Task, Habit, HabitLog, Notification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['custom_name', 'user', 'productivity_preference', 'onboarding_completed', 'created_at']
    list_filter = ['productivity_preference', 'onboarding_completed']
    search_fields = ['custom_name', 'user__username', 'user__email']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'due_date', 'is_completed', 'created_at']
    list_filter = ['is_completed', 'priority', 'reminder_set', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'description')
        }),
        ('Scheduling', {
            'fields': ('due_date', 'due_time', 'priority')
        }),
        ('Status', {
            'fields': ('is_completed', 'completed_at', 'reminder_set', 'reminder_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'frequency', 'reminder_time', 'is_active', 'created_at']
    list_filter = ['is_active', 'frequency', 'created_at']
    search_fields = ['title', 'goal_description', 'user__username']
    readonly_fields = ['created_at']


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ['habit', 'log_date', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'log_date']
    search_fields = ['habit__title', 'habit__user__username']
    date_hierarchy = 'log_date'
    readonly_fields = ['completed_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


# ===== MIGRATION INSTRUCTIONS =====
"""
To set up your database, run these commands in order:

1. Delete existing migrations (if you have any):
   - Delete all files in todo_app/migrations/ EXCEPT __init__.py

2. Create new migrations:
   python manage.py makemigrations

3. Apply migrations:
   python manage.py migrate

4. Create a superuser (for admin access):
   python manage.py createsuperuser

5. Run the development server:
   python manage.py runserver

6. Access the admin panel:
   http://127.0.0.1:8000/admin/

IMPORTANT NOTES:
- The UserProfile model has a OneToOne relationship with User
- Make sure to create a UserProfile for every user through onboarding
- The app uses Django's built-in User model for authentication
- All models include appropriate related_name for reverse lookups
- Habit streaks are calculated dynamically, not stored in the database

SAMPLE DATA (Optional):
After setting up, you can create sample data through the admin panel or Django shell:

python manage.py shell

from django.contrib.auth.models import User
from todo_app.models import UserProfile, Task, Habit
from datetime import date, timedelta

# Create a test user
user = User.objects.create_user('testuser', 'test@example.com', 'password123')

# Create profile
profile = UserProfile.objects.create(
    user=user,
    custom_name='Alex',
    productivity_preference='morning',
    onboarding_completed=True
)

# Create sample tasks
Task.objects.create(
    user=user,
    title='Finish project report',
    priority=1,
    due_date=date.today() + timedelta(days=2)
)

Task.objects.create(
    user=user,
    title='Buy groceries',
    priority=2,
    due_date=date.today()
)

# Create sample habits
Habit.objects.create(
    user=user,
    title='Drink Water',
    goal_description='Drink 2L of water daily',
    frequency='daily'
)

Habit.objects.create(
    user=user,
    title='Exercise',
    goal_description='30 minutes of exercise',
    frequency='daily'
)

print("Sample data created successfully!")
"""