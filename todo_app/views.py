# todo_app/views.py - COMPLETE UPDATED VERSION
# Replace your existing views.py with this version

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import (
    UserProfile, Task, Habit, HabitLog, Notification, Achievement,
    PRIORITY_CHOICES, PRODUCTIVITY_PREFERENCE, HABIT_FREQUENCY, THEME_MODES
)
from datetime import datetime, date, timedelta
import calendar
from calendar import monthcalendar
from django.views.decorators.csrf import csrf_exempt
import json


# --- FORMS (Keep existing forms, add settings form) ---
class RegisterForm:
    """Simple registration form."""
    def __init__(self, data=None):
        self.data = data or {}
        self.errors = {}
    
    def is_valid(self):
        username = self.data.get('username', '').strip()
        email = self.data.get('email', '').strip()
        password = self.data.get('password', '').strip()
        password2 = self.data.get('password2', '').strip()
        
        if not username:
            self.errors['username'] = 'Username is required'
        elif User.objects.filter(username=username).exists():
            self.errors['username'] = 'Username already exists'
        
        if not email:
            self.errors['email'] = 'Email is required'
        elif User.objects.filter(email=email).exists():
            self.errors['email'] = 'Email already registered'
        
        if not password:
            self.errors['password'] = 'Password is required'
        elif len(password) < 6:
            self.errors['password'] = 'Password must be at least 6 characters'
        
        if password != password2:
            self.errors['password2'] = 'Passwords do not match'
        
        return len(self.errors) == 0
    
    @property
    def cleaned_data(self):
        return {
            'username': self.data['username'].strip(),
            'email': self.data['email'].strip(),
            'password': self.data['password'].strip(),
        }


class TaskForm:
    """Form for adding/editing tasks."""
    def __init__(self, data=None):
        self.data = data or {}

    def is_valid(self):
        return 'title' in self.data and self.data['title'].strip() != ''

    @property
    def cleaned_data(self):
        try:
            priority_value = int(self.data.get('priority', 3))
        except ValueError:
            priority_value = 3

        return {
            'title': self.data.get('title', '').strip(),
            'description': self.data.get('description', '').strip(),
            'due_date': self.data.get('due_date') or None,
            'due_time': self.data.get('due_time') or None,
            'priority': priority_value,
            'reminder_set': self.data.get('reminder_set') == 'on',
        }


class HabitForm:
    """Form for adding/editing habits."""
    def __init__(self, data=None):
        self.data = data or {}

    def is_valid(self):
        return (
            'title' in self.data and self.data['title'].strip() != '' and
            'goal_description' in self.data and self.data['goal_description'].strip() != ''
        )

    @property
    def cleaned_data(self):
        return {
            'title': self.data.get('title', '').strip(),
            'goal_description': self.data.get('goal_description', '').strip(),
            'frequency': self.data.get('frequency', 'daily'),
            'reminder_time': self.data.get('reminder_time') or None,
        }


# --- AUTHENTICATION VIEWS (Keep existing) ---
def landing_view(request):
    """Landing page explaining the app."""
    if request.user.is_authenticated:
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile and profile.onboarding_completed:
            return redirect('dashboard')
        return redirect('onboarding_welcome')
    
    return render(request, 'todo_app/landing.html')


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('onboarding_welcome')
        else:
            for field, error in form.errors.items():
                messages.error(request, error)
    
    return render(request, 'todo_app/register.html')


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'todo_app/login.html')


@login_required
def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('landing')


# --- ONBOARDING VIEWS (Keep existing) ---
@login_required
def onboarding_welcome(request):
    """Step 1: Warm welcome and get user's name."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.onboarding_completed:
        return redirect('dashboard')
    
    if request.method == 'POST':
        custom_name = request.POST.get('custom_name', '').strip()
        if custom_name:
            profile.custom_name = custom_name
            profile.save()
            return redirect('onboarding_preference')
    
    return render(request, 'todo_app/onboarding_welcome.html')


@login_required
def onboarding_preference(request):
    """Step 2: Ask about morning/evening preference."""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        preference = request.POST.get('productivity_preference')
        if preference in ['morning', 'evening', 'anytime']:
            profile.productivity_preference = preference
            profile.save()
            return redirect('onboarding_habits')
    
    context = {
        'user_name': profile.custom_name,
        'preferences': PRODUCTIVITY_PREFERENCE,
    }
    return render(request, 'todo_app/onboarding_preference.html', context)


@login_required
def onboarding_habits(request):
    """Step 3: Ask about habits."""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        if 'skip' in request.POST:
            profile.onboarding_completed = True
            profile.save()
            return redirect('dashboard')
        
        # Process habit entries
        for key, value in request.POST.items():
            if key.startswith('habit_') and value.strip():
                Habit.objects.create(
                    user=request.user,
                    title=value.strip(),
                    goal_description=f"Complete {value.strip()} daily",
                    reminder_time=profile.get_recommended_time()
                )
        
        profile.onboarding_completed = True
        profile.save()
        
        # Create welcome notification
        Notification.objects.create(
            user=request.user,
            title="Welcome to TaskFlow! 🎉",
            message=f"Hey {profile.custom_name}! You're all set up. Let's crush those goals together!",
            notification_type='system'
        )
        
        return redirect('dashboard')
    
    context = {
        'user_name': profile.custom_name,
    }
    return render(request, 'todo_app/onboarding_habits.html', context)


# --- MAIN DASHBOARD (UPDATED WITH TAB FILTERING) ---
@login_required
def dashboard_view(request):
    """Main tasks dashboard with proper tab filtering."""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.onboarding_completed:
        return redirect('onboarding_welcome')
    
    # Get all tasks
    all_tasks = Task.objects.filter(user=request.user)
    
    # Filter by status
    active_tasks = all_tasks.filter(is_completed=False).order_by('priority', 'due_date')
    completed_tasks = all_tasks.filter(is_completed=True).order_by('-completed_at')
    
    # Needs Attention: Overdue OR High priority incomplete tasks
    attention_tasks = active_tasks.filter(
        Q(due_date__lt=date.today()) | Q(priority=1)
    ).distinct()
    
    context = {
        'user_name': profile.custom_name,
        'all_tasks': all_tasks,
        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,
        'attention_tasks': attention_tasks,
        'active_count': active_tasks.count(),
        'completed_count': completed_tasks.count(),
        'needs_attention_count': attention_tasks.count(),
        'priorities': PRIORITY_CHOICES,
    }
    return render(request, 'todo_app/dashboard.html', context)


# --- HABITS VIEW (UPDATED) ---
@login_required
@login_required
def habits_view(request):
    """Habits dashboard with correct frequency-based progress tracking."""
    profile = get_object_or_404(UserProfile, user=request.user)

    if not profile.onboarding_completed:
        return redirect('onboarding_welcome')

    today = date.today()
    user_habits = Habit.objects.filter(user=request.user, is_active=True)

    # Total streak
    total_streak = sum(h.get_streak() for h in user_habits)

    # Completed today
    habits_completed_today = [
        h for h in user_habits if h.logs.filter(log_date=today).exists()
    ]

    habits_with_progress = []
    for habit in user_habits:

        # Add frequency-based progress
        if habit.frequency == 'daily':
            habit.progress = habit.last_7_days()
        elif habit.frequency == 'weekly':
            habit.progress = habit.last_4_weeks()
        elif habit.frequency == 'monthly':
            habit.progress = habit.last_3_months()
        else:
            habit.progress = []  # For quarterly/custom you may expand later

        habits_with_progress.append(habit)

    context = {
        'user_name': profile.custom_name,
        'user_habits': habits_with_progress,
        'total_streak': total_streak,
        'habits_completed_today': habits_completed_today,
        'total_habits': user_habits.count(),
        'habit_frequencies': HABIT_FREQUENCY,
    }
    return render(request, 'todo_app/habits_view.html', context)



# --- CALENDAR VIEW ---
@login_required
def calendar_view(request):
    """Calendar view with tasks."""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if not profile.onboarding_completed:
        return redirect('onboarding_welcome')
    
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    month_name = calendar.month_name[month]
    cal = monthcalendar(year, month)
    
    # Get all tasks for this month
    month_tasks = Task.objects.filter(
        user=request.user,
        due_date__year=year,
        due_date__month=month
    )
    
    # Build calendar with tasks
    calendar_weeks = []
    for week in cal:
        calendar_week = []
        for day_num in week:
            if day_num == 0:
                calendar_week.append({
                    'day': '',
                    'in_month': False,
                    'is_today': False,
                    'tasks': []
                })
            else:
                day_date = date(year, month, day_num)
                day_tasks = month_tasks.filter(due_date=day_date)
                
                calendar_week.append({
                    'day': day_num,
                    'in_month': True,
                    'is_today': day_date == today,
                    'tasks': day_tasks,
                    'date': day_date
                })
        calendar_weeks.append(calendar_week)
    
    context = {
        'user_name': profile.custom_name,
        'current_month': month_name,
        'current_year': year,
        'current_month_num': month,
        'calendar_weeks': calendar_weeks,
    }
    return render(request, 'todo_app/calendar_view.html', context)


# --- SETTINGS VIEW (NEW) ---
# Replace the settings_view function in views.py with this:

@login_required
def settings_view(request):
    """Settings page with theme and color customization."""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        # Handle color customization
        if 'apply_colors' in request.POST:
            primary = request.POST.get('primary_color', profile.primary_color)
            secondary = request.POST.get('secondary_color', profile.secondary_color)
            accent = request.POST.get('accent_color', profile.accent_color)
            
            # Validate hex colors
            import re
            hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
            
            if hex_pattern.match(primary):
                profile.primary_color = primary
            if hex_pattern.match(secondary):
                profile.secondary_color = secondary
            if hex_pattern.match(accent):
                profile.accent_color = accent
            
            profile.save()
            messages.success(request, 'Colors applied successfully!')
            return redirect('settings_view')
        
        # Handle reset to default
        if 'reset_colors' in request.POST:
            profile.primary_color = '#3b82f6'
            profile.secondary_color = '#8b5cf6'
            profile.accent_color = '#ec4899'
            profile.save()
            messages.success(request, 'Colors reset to default!')
            return redirect('settings_view')
    
    context = {
        'user_name': profile.custom_name,
        'profile': profile,
        'theme_modes': THEME_MODES,
    }
    return render(request, 'todo_app/settings.html', context)


# Also ensure your update_theme_ajax function looks like this:

@login_required
@csrf_exempt
def update_theme_ajax(request):
    """AJAX endpoint for live theme updates."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = request.user.profile
            
            # Update theme mode
            theme_mode = data.get('theme_mode')
            if theme_mode in ['light', 'dark', 'night']:
                profile.theme_mode = theme_mode
                profile.save()
            
            # Update colors
            primary = data.get('primary_color')
            secondary = data.get('secondary_color')
            accent = data.get('accent_color')
            
            import re
            hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
            
            if primary and hex_pattern.match(primary):
                profile.primary_color = primary
            if secondary and hex_pattern.match(secondary):
                profile.secondary_color = secondary
            if accent and hex_pattern.match(accent):
                profile.accent_color = accent
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'theme_mode': profile.theme_mode,
                'primary_color': profile.primary_color,
                'secondary_color': profile.secondary_color,
                'accent_color': profile.accent_color
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# --- TASK CRUD (UPDATED) ---
@login_required
@require_POST
def add_task(request):
    """Add a new task."""
    form = TaskForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        Task.objects.create(
            user=request.user,
            title=data['title'],
            description=data['description'],
            due_date=data['due_date'],
            due_time=data['due_time'],
            priority=data['priority'],
            reminder_set=data['reminder_set'],
        )
        messages.success(request, f'Task "{data["title"]}" added successfully!')
    else:
        messages.error(request, 'Please provide a task title.')
    
    return redirect('dashboard')


@login_required
@require_POST
def complete_task(request, task_id):
    """Toggle task completion."""
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.is_completed = not task.is_completed
    if task.is_completed:
        task.completed_at = timezone.now()
    else:
        task.completed_at = None
    task.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
@require_POST
def delete_task(request, task_id):
    """Delete a task."""
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    title = task.title
    task.delete()
    messages.success(request, f'Task "{title}" deleted.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


# --- HABIT CRUD (UPDATED) ---
@login_required
@require_POST
def add_habit(request):
    """Add a new habit."""
    form = HabitForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        profile = request.user.profile
        
        Habit.objects.create(
            user=request.user,
            title=data['title'],
            goal_description=data['goal_description'],
            frequency=data['frequency'],
            reminder_time=data['reminder_time'] or profile.get_recommended_time(),
        )
        messages.success(request, f'Habit "{data["title"]}" added successfully!')
    else:
        messages.error(request, 'Please fill in all habit details.')
    
    return redirect('habits_view')


@login_required
@require_POST
def complete_habit(request, habit_id):
    """Mark habit as complete (with overachievement support)."""
    habit = get_object_or_404(Habit, pk=habit_id, user=request.user)
    today = date.today()
    
    log, created = HabitLog.objects.get_or_create(
        habit=habit,
        log_date=today,
        defaults={'completion_count': 1, 'is_completed': True, 'completed_at': timezone.now()}
    )
    
    if not created:
        # Increment count for overachievement
       # ✅ Updated logic — no target_count
        log.completion_count += 1
        log.is_completed = True
        log.completed_at = timezone.now()
        log.save()

    
    # Check for achievements
    streak = habit.get_streak()
    if streak == 7:
        Achievement.objects.create(
            user=request.user,
            title="Week Warrior! 🔥",
            description=f"Maintained a 7-day streak for '{habit.title}'",
            badge_icon="🔥",
            related_habit=habit
        )
        messages.success(request, f"Achievement unlocked: Week Warrior! 7-day streak for {habit.title}!")
    elif streak == 30:
        Achievement.objects.create(
            user=request.user,
            title="Month Master! 🏆",
            description=f"Maintained a 30-day streak for '{habit.title}'",
            badge_icon="🏆",
            related_habit=habit
        )
        messages.success(request, f"Achievement unlocked: Month Master! 30-day streak for {habit.title}!")
    
    return redirect('habits_view')


@login_required
@require_POST
def delete_habit(request, habit_id):
    """Delete a habit."""
    habit = get_object_or_404(Habit, pk=habit_id, user=request.user)
    title = habit.title
    habit.delete()
    messages.success(request, f'Habit "{title}" deleted.')
    return redirect('habits_view')


# --- UTILITY FUNCTION ---
def get_time_of_day():
    """Returns a greeting based on the current time."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    return "evening"


# Add this view at the end of views.py
@login_required
@csrf_exempt
def update_theme_ajax(request):
    """AJAX endpoint for live theme updates."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            profile = request.user.profile
            
            theme_mode = data.get('theme_mode')
            if theme_mode in ['light', 'dark', 'night']:
                profile.theme_mode = theme_mode
            
            primary = data.get('primary_color')
            secondary = data.get('secondary_color')
            accent = data.get('accent_color')
            
            if primary and primary.startswith('#') and len(primary) == 7:
                profile.primary_color = primary
            if secondary and secondary.startswith('#') and len(secondary) == 7:
                profile.secondary_color = secondary
            if accent and accent.startswith('#') and len(accent) == 7:
                profile.accent_color = accent
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'theme_mode': profile.theme_mode,
                'primary_color': profile.primary_color,
                'secondary_color': profile.secondary_color,
                'accent_color': profile.accent_color
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def edit_task(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        # Update task fields
        task.title = request.POST.get('title', '').strip()
        task.description = request.POST.get('description', '').strip()
        task.due_date = request.POST.get('due_date') or None
        task.due_time = request.POST.get('due_time') or None
        task.priority = request.POST.get('priority', 2)
        
        # Validate title
        if not task.title:
            messages.error(request, 'Task title cannot be empty.')
            return redirect('dashboard')
        
        task.save()
        messages.success(request, 'Task updated successfully!')
        return redirect('dashboard')
    
    return redirect('dashboard')