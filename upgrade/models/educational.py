# Complete Educational Models
"""
مدل‌های کامل سیستم آموزشی
ترکیب همه فازها
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import json


class Subject(models.Model):
    """دروس تحصیلی"""
    name = models.CharField(max_length=50, unique=True)
    persian_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, default='book')
    grade_levels = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'دروس'
        ordering = ['order', 'persian_name']
    
    def __str__(self):
        return self.persian_name


class StudentProfile(models.Model):
    """پروفایل دانش‌آموز"""
    SCHOOL_TYPES = [
        ('public', 'دولتی'),
        ('private', 'غیرانتفاعی'),
        ('sampad', 'تیزهوشان'),
        ('other', 'سایر'),
    ]
    
    LEARNING_STYLES = [
        ('visual', 'بصری'),
        ('auditory', 'شنیداری'),
        ('kinesthetic', 'حرکتی'),
        ('mixed', 'ترکیبی'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    grade_level = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES, default='public')
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, default='visual')
    daily_study_goal = models.PositiveIntegerField(default=60)
    total_points = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    study_streak = models.PositiveIntegerField(default=0)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def add_points(self, points, reason=""):
        """اضافه کردن امتیاز"""
        old_level = self.current_level
        self.total_points += points
        new_level = (self.total_points // 100) + 1
        
        level_up = new_level > old_level
        if level_up:
            self.current_level = new_level
        
        self.save()
        return {'points_added': points, 'level_up': level_up}


class Homework(models.Model):
    """تکالیف"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('completed', 'تکمیل شده'),
        ('overdue', 'عقب‌افتاده'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='homeworks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    difficulty = models.PositiveSmallIntegerField(choices=[(i, f"{i}⭐") for i in range(1, 6)], default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    score = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now() and self.status != 'completed'
    
    def mark_completed(self, score=None):
        """تکمیل تکلیف"""
        self.status = 'completed'
        if score:
            self.score = score
        self.save()
        
        points = self.difficulty * 10
        return self.student.add_points(points, f"تکلیف {self.title}")


class Achievement(models.Model):
    """دستاوردها"""
    name = models.CharField(max_length=100, unique=True)
    persian_name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='trophy')
    points_reward = models.PositiveIntegerField(default=50)
    condition = models.JSONField()
    is_active = models.BooleanField(default=True)


class ParentProfile(models.Model):
    """پروفایل والدین"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    children = models.ManyToManyField(StudentProfile, related_name='parents')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    weekly_report = models.BooleanField(default=True)


class ParentalControl(models.Model):
    """کنترل والدین"""
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='parental_control')
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    daily_time_limit = models.PositiveIntegerField(default=120)
    content_filter_level = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)


# سایر مدل‌ها...