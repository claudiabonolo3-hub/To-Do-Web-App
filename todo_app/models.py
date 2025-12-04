# todo_app/models.py - UPDATED VERSION
from django.db import models
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from django.utils import timezone
import calendar

# Tuple for Task Priority choices
PRIORITY_CHOICES = [
    (1, 'High Priority'),
    (2, 'Medium Priority'),
    (3, 'Low Priority'),
]

PRODUCTIVITY_PREFERENCE = [
    ('morning', 'Morning Person'),
    ('evening', 'Evening Person'),
    ('anytime', 'No Preference'),
]

# UPDATED: Added Monthly, Quarterly, Custom
HABIT_FREQUENCY = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('custom', 'Custom'),
]

# NEW: Theme modes
THEME_MODES = [
    ('light', 'Light Mode'),
    ('dark', 'Dark Mode'),
    ('night', 'Night Mode'),
]


class UserProfile(models.Model):
    """
    Extended user profile with personalization settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    custom_name = models.CharField(max_length=100, default='User')
    productivity_preference = models.CharField(
        max_length=20, 
        choices=PRODUCTIVITY_PREFERENCE,
        default='anytime',
        help_text="When are you most productive?"
    )
    onboarding_completed = models.BooleanField(default=False)
    
    # NEW: Theme and color preferences
    theme_mode = models.CharField(max_length=20, choices=THEME_MODES, default='light')
    primary_color = models.CharField(max_length=7, default='#3b82f6')  # Blue
    secondary_color = models.CharField(max_length=7, default='#8b5cf6')  # Purple
    accent_color = models.CharField(max_length=7, default='#ec4899')  # Pink
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.custom_name} ({self.user.username})"
    
    def get_recommended_time(self):
        """Returns recommended time based on productivity preference."""
        if self.productivity_preference == 'morning':
            return time(8, 0)  # 8:00 AM
        elif self.productivity_preference == 'evening':
            return time(18, 0)  # 6:00 PM
        return time(12, 0)  # Noon


class Task(models.Model):
    """Represents a one-time task."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    due_time = models.TimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=3)
    reminder_set = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['is_completed', 'priority', 'due_date', 'due_time', 'created_at']
    
    def __str__(self):
        return self.title
    
    def get_priority_display_color(self):
        """Returns a CSS class for priority color/badge."""
        if self.priority == 1:
            return 'priority-high'
        elif self.priority == 2:
            return 'priority-medium'
        return 'priority-low'
    
    def is_overdue(self):
        """Check if task is overdue."""
        if not self.due_date or self.is_completed:
            return False
        return self.due_date < date.today()
    
    def get_progress_percentage(self):
        """Calculate task progress based on time remaining."""
        if not self.due_date or self.is_completed:
            return 0
        
        today = date.today()
        if self.due_date < today:
            return 100  # Overdue
        
        # Calculate days remaining
        days_total = (self.due_date - self.created_at.date()).days
        days_passed = (today - self.created_at.date()).days
        
        if days_total <= 0:
            return 0
        
        return min(int((days_passed / days_total) * 100), 100)


class Habit(models.Model):
    """Represents a recurring habit."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    title = models.CharField(max_length=200)
    goal_description = models.TextField(help_text="e.g., Drinking 2l of water daily")
    frequency = models.CharField(
        max_length=20,
        choices=HABIT_FREQUENCY,
        default='daily'
    )

    # ❌ REMOVE target_count
    # target_count = models.IntegerField(default=1)

    reminder_time = models.TimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_frequency_display()})"

    # --- NEW METHODS ADDED ---

    def last_7_days(self):
        """Returns progress for last 7 days (for daily habits)."""
        today = timezone.now().date()
        days = []

        for i in range(6, -1, -1):
            date_check = today - timedelta(days=i)
            completed = self.logs.filter(log_date=date_check).exists()

            days.append({
                'date': date_check,
                'day_initial': date_check.strftime('%a')[0],
                'completed': completed,
                'is_today': date_check == today
            })
        return days

    def last_4_weeks(self):
        """Returns progress for last 4 weeks (for weekly habits)."""
        today = timezone.now().date()
        weeks = []

        for i in range(3, -1, -1):
            week_start = today - timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)

            completed = self.logs.filter(
                log_date__range=[week_start, week_end]
            ).exists()

            weeks.append({
                'week_start': week_start,
                'week_end': week_end,
                'week_num': week_start.isocalendar()[1],
                'completed': completed,
                'is_current': week_start <= today <= week_end
            })
        return weeks

    def last_3_months(self):
        """Returns progress for last 3 months (for monthly habits)."""
        today = timezone.now().date()
        months = []

        for i in range(2, -1, -1):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1

            _, last_day = calendar.monthrange(year, month)

            month_start = date(year, month, 1)
            month_end = date(year, month, last_day)

            completed = self.logs.filter(
                log_date__range=[month_start, month_end]
            ).exists()

            month_name = calendar.month_name[month]

            months.append({
                'month_start': month_start,
                'month_end': month_end,
                'month_name': month_name,
                'month_initial': month_name[:3],
                'completed': completed,
                'is_current': (today.month == month and today.year == year)
            })
        return months

    def get_streak(self):
            """
            Returns the current streak of consecutive habit completions.
            Supports daily, weekly, and monthly habits.
            """
            logs = self.logs.filter(is_completed=True).order_by('-log_date')

            if not logs.exists():
                return 0

            streak = 1
            prev_date = logs[0].log_date

            for log in logs[1:]:
                curr = log.log_date

                if self.frequency == 'daily':
                    expected = prev_date - timedelta(days=1)

                elif self.frequency == 'weekly':
                    expected = prev_date - timedelta(weeks=1)

                elif self.frequency == 'monthly':
                    month = prev_date.month - 1
                    year = prev_date.year
                    if month <= 0:
                        month += 12
                        year -= 1

                    day = min(prev_date.day, calendar.monthrange(year, month)[1])
                    expected = date(year, month, day)

                else:
                    break

                if curr == expected:
                    streak += 1
                    prev_date = curr
                else:
                    break

            return streak

class HabitLog(models.Model):
    """Logs the completion status of a habit for a specific day."""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    log_date = models.DateField(default=date.today)
    is_completed = models.BooleanField(default=False)
    # NEW: Support for overachievement
    completion_count = models.IntegerField(default=0, help_text="Number of times completed")
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('habit', 'log_date')
        ordering = ['-log_date']
    
    def __str__(self):
        status = "✓" if self.is_completed else "✗"
        return f"{self.habit.title} on {self.log_date} {status}"


class Notification(models.Model):
    """Stores user notifications and reminders."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('task', 'Task Reminder'),
            ('habit', 'Habit Reminder'),
            ('achievement', 'Achievement'),
            ('system', 'System Message'),
        ],
        default='system'
    )
    related_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE)
    related_habit = models.ForeignKey(Habit, null=True, blank=True, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} for {self.user.username}"


# NEW: Achievement tracking
class Achievement(models.Model):
    """Track user achievements and milestones."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField()
    badge_icon = models.CharField(max_length=50, default='🏆')
    earned_at = models.DateTimeField(auto_now_add=True)
    related_habit = models.ForeignKey(Habit, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"