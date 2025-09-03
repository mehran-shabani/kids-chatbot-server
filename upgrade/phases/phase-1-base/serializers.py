# educational/serializers.py - Phase 1 Base Serializers
"""
Serializers برای API‌های آموزشی فاز 1
"""

from rest_framework import serializers
from django.utils import timezone
from .models import StudentProfile, Subject, Homework, HomeworkHelp, DailyActivity


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer برای دروس تحصیلی"""
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'persian_name', 'description', 
            'color_code', 'icon', 'grade_levels'
        ]
        read_only_fields = ['id']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer برای پروفایل دانش‌آموز"""
    age = serializers.ReadOnlyField()
    next_level_points = serializers.ReadOnlyField()
    preferred_subjects = SubjectSerializer(many=True, read_only=True)
    preferred_subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        many=True,
        write_only=True,
        source='preferred_subjects'
    )
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'grade_level', 'school_type', 'school_name', 'academic_year',
            'birth_date', 'gender', 'learning_style', 'daily_study_goal',
            'total_points', 'current_level', 'study_streak', 'avatar_url',
            'theme_preference', 'notification_homework', 'notification_achievement',
            'notification_daily_reminder', 'age', 'next_level_points',
            'preferred_subjects', 'preferred_subject_ids', 'weak_subjects',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_points', 'current_level', 'study_streak',
            'created_at', 'updated_at'
        ]
    
    def validate_grade_level(self, value):
        """اعتبارسنجی پایه تحصیلی"""
        if not 1 <= value <= 12:
            raise serializers.ValidationError("پایه تحصیلی باید بین 1 تا 12 باشد")
        return value
    
    def validate_birth_date(self, value):
        """اعتبارسنجی تاریخ تولد"""
        if value:
            today = timezone.now().date()
            age = today.year - value.year
            if age < 5 or age > 20:
                raise serializers.ValidationError("سن باید بین 5 تا 20 سال باشد")
        return value
    
    def validate_daily_study_goal(self, value):
        """اعتبارسنجی هدف مطالعه روزانه"""
        if value < 15 or value > 480:  # 15 دقیقه تا 8 ساعت
            raise serializers.ValidationError("هدف مطالعه روزانه باید بین 15 دقیقه تا 8 ساعت باشد")
        return value


class HomeworkSerializer(serializers.ModelSerializer):
    """Serializer برای تکالیف"""
    subject_name = serializers.CharField(source='subject.persian_name', read_only=True)
    subject_color = serializers.CharField(source='subject.color_code', read_only=True)
    subject_icon = serializers.CharField(source='subject.icon', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    time_remaining = serializers.ReadOnlyField()
    points_value = serializers.ReadOnlyField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Homework
        fields = [
            'id', 'title', 'description', 'instructions',
            'subject', 'subject_name', 'subject_color', 'subject_icon',
            'assigned_date', 'due_date', 'estimated_minutes',
            'difficulty', 'difficulty_display', 'status', 'status_display',
            'priority', 'completion_date', 'score', 'feedback',
            'attachment_url', 'submission_url', 'is_overdue',
            'time_remaining', 'points_value', 'view_count'
        ]
        read_only_fields = [
            'id', 'assigned_date', 'completion_date', 'view_count'
        ]
    
    def validate_due_date(self, value):
        """اعتبارسنجی موعد تحویل"""
        if value <= timezone.now():
            raise serializers.ValidationError("موعد تحویل باید در آینده باشد")
        return value
    
    def validate_estimated_minutes(self, value):
        """اعتبارسنجی زمان تخمینی"""
        if value < 5 or value > 480:  # 5 دقیقه تا 8 ساعت
            raise serializers.ValidationError("زمان تخمینی باید بین 5 دقیقه تا 8 ساعت باشد")
        return value


class HomeworkCreateSerializer(serializers.ModelSerializer):
    """Serializer ساده برای ایجاد تکلیف"""
    
    class Meta:
        model = Homework
        fields = [
            'title', 'description', 'subject', 'due_date', 
            'estimated_minutes', 'difficulty', 'priority'
        ]
    
    def create(self, validated_data):
        """ایجاد تکلیف جدید"""
        # student از context دریافت می‌شود
        student = self.context['student']
        return Homework.objects.create(student=student, **validated_data)


class HomeworkUpdateSerializer(serializers.ModelSerializer):
    """Serializer برای به‌روزرسانی تکلیف"""
    
    class Meta:
        model = Homework
        fields = [
            'title', 'description', 'instructions', 'due_date',
            'estimated_minutes', 'difficulty', 'priority', 'status'
        ]
    
    def validate_status(self, value):
        """اعتبارسنجی تغییر وضعیت"""
        if self.instance and self.instance.status == 'completed' and value != 'completed':
            raise serializers.ValidationError("نمی‌توان تکلیف تکمیل شده را به حالت قبل برگرداند")
        return value


class HomeworkHelpSerializer(serializers.ModelSerializer):
    """Serializer برای درخواست کمک"""
    homework_title = serializers.CharField(source='homework.title', read_only=True)
    
    class Meta:
        model = HomeworkHelp
        fields = [
            'id', 'homework', 'homework_title', 'question', 
            'ai_response', 'is_helpful', 'additional_notes', 'created_at'
        ]
        read_only_fields = ['id', 'ai_response', 'created_at']


class DailyActivitySerializer(serializers.ModelSerializer):
    """Serializer برای فعالیت روزانه"""
    subjects_studied_names = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyActivity
        fields = [
            'date', 'study_minutes', 'homeworks_completed',
            'questions_asked', 'points_earned', 'subjects_studied',
            'subjects_studied_names', 'peak_activity_hour'
        ]
    
    def get_subjects_studied_names(self, obj):
        """دریافت نام دروس مطالعه شده"""
        if obj.subjects_studied:
            subjects = Subject.objects.filter(id__in=obj.subjects_studied)
            return [s.persian_name for s in subjects]
        return []


class StudentDashboardSerializer(serializers.Serializer):
    """Serializer برای داشبورد دانش‌آموز"""
    profile = StudentProfileSerializer(read_only=True)
    stats = serializers.DictField(read_only=True)
    today_homeworks = HomeworkSerializer(many=True, read_only=True)
    recent_activities = DailyActivitySerializer(many=True, read_only=True)
    achievements = serializers.ListField(read_only=True)  # فاز بعدی
    
    class Meta:
        fields = [
            'profile', 'stats', 'today_homeworks', 
            'recent_activities', 'achievements'
        ]


class WeeklyReportSerializer(serializers.Serializer):
    """Serializer برای گزارش هفتگی"""
    week_start = serializers.DateField(read_only=True)
    week_end = serializers.DateField(read_only=True)
    total_study_minutes = serializers.IntegerField(read_only=True)
    homeworks_completed = serializers.IntegerField(read_only=True)
    homeworks_total = serializers.IntegerField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    points_earned = serializers.IntegerField(read_only=True)
    best_subject = serializers.CharField(read_only=True)
    needs_improvement = serializers.CharField(read_only=True)
    daily_breakdown = DailyActivitySerializer(many=True, read_only=True)
    
    class Meta:
        fields = [
            'week_start', 'week_end', 'total_study_minutes',
            'homeworks_completed', 'homeworks_total', 'completion_rate',
            'points_earned', 'best_subject', 'needs_improvement',
            'daily_breakdown'
        ]


# Helper Serializers برای validation
class BulkHomeworkCreateSerializer(serializers.Serializer):
    """Serializer برای ایجاد چندین تکلیف همزمان"""
    homeworks = HomeworkCreateSerializer(many=True)
    
    def create(self, validated_data):
        """ایجاد چندین تکلیف"""
        homeworks_data = validated_data['homeworks']
        student = self.context['student']
        
        homeworks = []
        for homework_data in homeworks_data:
            homework = Homework.objects.create(student=student, **homework_data)
            homeworks.append(homework)
        
        return {'homeworks': homeworks}


class SubjectProgressSerializer(serializers.Serializer):
    """Serializer برای پیشرفت در هر درس"""
    subject = SubjectSerializer(read_only=True)
    total_homeworks = serializers.IntegerField(read_only=True)
    completed_homeworks = serializers.IntegerField(read_only=True)
    average_score = serializers.FloatField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)
    last_activity = serializers.DateTimeField(read_only=True)
    
    class Meta:
        fields = [
            'subject', 'total_homeworks', 'completed_homeworks',
            'average_score', 'completion_rate', 'last_activity'
        ]