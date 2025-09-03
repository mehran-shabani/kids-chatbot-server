# educational/models.py - Phase 1 Base Models
"""
مدل‌های پایه‌ای برای سیستم آموزشی
این فایل در فاز 1 به پروژه اضافه می‌شود
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Subject(models.Model):
    """مدل دروس تحصیلی"""
    name = models.CharField(max_length=50, unique=True, help_text="نام انگلیسی درس")
    persian_name = models.CharField(max_length=100, help_text="نام فارسی درس")
    description = models.TextField(blank=True, help_text="توضیحات درس")
    color_code = models.CharField(max_length=7, default='#007bff', help_text="کد رنگ هگز")
    icon = models.CharField(max_length=50, default='book', help_text="نام آیکون")
    grade_levels = models.JSONField(
        default=list, 
        help_text="لیست پایه‌های تحصیلی مجاز - مثال: [1,2,3,4,5,6]"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'دروس'
        ordering = ['order', 'persian_name']
    
    def __str__(self):
        return self.persian_name
    
    def is_available_for_grade(self, grade_level):
        """بررسی در دسترس بودن درس برای پایه مشخص"""
        return grade_level in self.grade_levels


class StudentProfile(models.Model):
    """پروفایل تحصیلی دانش‌آموز"""
    
    SCHOOL_TYPES = [
        ('public', 'دولتی'),
        ('private', 'غیرانتفاعی'),
        ('sampad', 'نمونه دولتی (تیزهوشان)'),
        ('international', 'بین‌المللی'),
        ('other', 'سایر'),
    ]
    
    LEARNING_STYLES = [
        ('visual', 'بصری - یادگیری با دیدن'),
        ('auditory', 'شنیداری - یادگیری با شنیدن'),
        ('kinesthetic', 'حرکتی - یادگیری با انجام'),
        ('reading', 'مطالعه - یادگیری با خواندن'),
        ('mixed', 'ترکیبی - همه روش‌ها'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'پسر'),
        ('F', 'دختر'),
        ('O', 'ترجیح می‌دهم نگویم'),
    ]
    
    # ارتباط با کاربر
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='کاربر'
    )
    
    # اطلاعات تحصیلی
    grade_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name='پایه تحصیلی'
    )
    school_type = models.CharField(
        max_length=20, 
        choices=SCHOOL_TYPES, 
        default='public',
        verbose_name='نوع مدرسه'
    )
    school_name = models.CharField(max_length=200, blank=True, verbose_name='نام مدرسه')
    academic_year = models.CharField(max_length=10, blank=True, verbose_name='سال تحصیلی')
    
    # اطلاعات شخصی
    birth_date = models.DateField(null=True, blank=True, verbose_name='تاریخ تولد')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='جنسیت')
    learning_style = models.CharField(
        max_length=20, 
        choices=LEARNING_STYLES, 
        default='visual',
        verbose_name='سبک یادگیری'
    )
    
    # تنظیمات مطالعه
    daily_study_goal = models.PositiveIntegerField(
        default=60, 
        help_text="هدف مطالعه روزانه به دقیقه",
        verbose_name='هدف مطالعه روزانه (دقیقه)'
    )
    preferred_subjects = models.ManyToManyField(
        Subject, 
        blank=True,
        verbose_name='دروس مورد علاقه'
    )
    weak_subjects = models.JSONField(
        default=list,
        help_text="لیست دروسی که دانش‌آموز در آن‌ها ضعیف است",
        verbose_name='دروس نیازمند تقویت'
    )
    
    # گیمیفیکیشن پایه
    total_points = models.PositiveIntegerField(default=0, verbose_name='کل امتیازات')
    current_level = models.PositiveIntegerField(default=1, verbose_name='سطح فعلی')
    study_streak = models.PositiveIntegerField(
        default=0, 
        help_text="تعداد روزهای متوالی مطالعه",
        verbose_name='روزهای متوالی مطالعه'
    )
    last_activity_date = models.DateField(auto_now=True, verbose_name='آخرین فعالیت')
    
    # شخصی‌سازی UI
    avatar_url = models.URLField(blank=True, verbose_name='آواتار')
    theme_preference = models.CharField(
        max_length=20, 
        default='default',
        verbose_name='تم مورد علاقه'
    )
    
    # تنظیمات اعلانات
    notification_homework = models.BooleanField(default=True, verbose_name='اعلان تکالیف')
    notification_achievement = models.BooleanField(default=True, verbose_name='اعلان دستاوردها')
    notification_daily_reminder = models.BooleanField(default=True, verbose_name='یادآور روزانه')
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'پروفایل دانش‌آموز'
        verbose_name_plural = 'پروفایل‌های دانش‌آموزان'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - پایه {self.grade_level}"
    
    @property
    def age(self):
        """محاسبه سن دانش‌آموز"""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    @property
    def next_level_points(self):
        """امتیاز مورد نیاز برای سطح بعدی"""
        from django.conf import settings
        level_up_points = getattr(settings, 'EDUCATIONAL_SETTINGS', {}).get('LEVEL_UP_POINTS', 100)
        return (self.current_level * level_up_points) - self.total_points
    
    def add_points(self, points, reason=""):
        """اضافه کردن امتیاز و بررسی سطح جدید"""
        old_level = self.current_level
        self.total_points += points
        
        # محاسبه سطح جدید
        from django.conf import settings
        level_up_points = getattr(settings, 'EDUCATIONAL_SETTINGS', {}).get('LEVEL_UP_POINTS', 100)
        new_level = (self.total_points // level_up_points) + 1
        
        level_up = False
        if new_level > self.current_level:
            self.current_level = new_level
            level_up = True
        
        self.save()
        
        return {
            'points_added': points,
            'total_points': self.total_points,
            'level_up': level_up,
            'old_level': old_level,
            'new_level': self.current_level,
            'reason': reason
        }
    
    def update_study_streak(self):
        """به‌روزرسانی رکورد مطالعه متوالی"""
        today = timezone.now().date()
        
        if self.last_activity_date == today:
            return self.study_streak  # امروز قبلاً فعالیت کرده
        
        if self.last_activity_date == today - timezone.timedelta(days=1):
            # دیروز فعالیت کرده، رکورد ادامه دارد
            self.study_streak += 1
        else:
            # رکورد شکسته شده
            self.study_streak = 1
        
        self.last_activity_date = today
        self.save()
        return self.study_streak


class Homework(models.Model):
    """مدل تکالیف دانش‌آموزان"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار انجام'),
        ('in_progress', 'در حال انجام'),
        ('completed', 'تکمیل شده'),
        ('overdue', 'گذشته از موعد'),
        ('reviewed', 'بررسی شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    DIFFICULTY_CHOICES = [
        (1, '⭐ آسان'),
        (2, '⭐⭐ متوسط'),
        (3, '⭐⭐⭐ سخت'),
        (4, '⭐⭐⭐⭐ خیلی سخت'),
        (5, '⭐⭐⭐⭐⭐ چالشی'),
    ]
    
    # روابط
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='homeworks',
        verbose_name='دانش‌آموز'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE,
        verbose_name='درس'
    )
    
    # محتوای تکلیف
    title = models.CharField(max_length=200, verbose_name='عنوان تکلیف')
    description = models.TextField(verbose_name='شرح تکلیف')
    instructions = models.TextField(
        blank=True, 
        help_text="راهنمای انجام تکلیف",
        verbose_name='راهنمای انجام'
    )
    
    # زمان‌بندی
    assigned_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ تعیین')
    due_date = models.DateTimeField(verbose_name='مهلت انجام')
    estimated_minutes = models.PositiveIntegerField(
        default=30,
        help_text="تخمین زمان انجام به دقیقه",
        verbose_name='زمان تخمینی (دقیقه)'
    )
    
    # ویژگی‌های تکلیف
    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_CHOICES, 
        default=2,
        verbose_name='سطح سختی'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='وضعیت'
    )
    priority = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=کم، 5=خیلی زیاد",
        verbose_name='اولویت'
    )
    
    # نتایج و ارزیابی
    completion_date = models.DateTimeField(
        null=True, blank=True,
        verbose_name='تاریخ تکمیل'
    )
    score = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='نمره (0-100)'
    )
    feedback = models.TextField(blank=True, verbose_name='بازخورد')
    teacher_notes = models.TextField(blank=True, verbose_name='یادداشت معلم')
    
    # فایل‌ها و ضمائم
    attachment_url = models.URLField(blank=True, verbose_name='فایل ضمیمه')
    submission_url = models.URLField(blank=True, verbose_name='فایل ارسالی')
    
    # آمار
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    help_requested = models.BooleanField(default=False, verbose_name='درخواست کمک')
    
    class Meta:
        verbose_name = 'تکلیف'
        verbose_name_plural = 'تکالیف'
        ordering = ['-due_date', '-priority']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['subject', 'grade_level']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"
    
    @property
    def is_overdue(self):
        """بررسی عقب‌افتادگی از موعد"""
        return (
            self.due_date < timezone.now() and 
            self.status not in ['completed', 'reviewed', 'cancelled']
        )
    
    @property
    def time_remaining(self):
        """زمان باقی‌مانده تا موعد"""
        if self.status in ['completed', 'reviewed', 'cancelled']:
            return None
        
        delta = self.due_date - timezone.now()
        if delta.total_seconds() <= 0:
            return "گذشته از موعد"
        
        days = delta.days
        hours = delta.seconds // 3600
        
        if days > 0:
            return f"{days} روز و {hours} ساعت"
        elif hours > 0:
            return f"{hours} ساعت"
        else:
            minutes = (delta.seconds % 3600) // 60
            return f"{minutes} دقیقه"
    
    @property
    def points_value(self):
        """محاسبه امتیاز تکلیف بر اساس سختی"""
        from django.conf import settings
        points_map = getattr(settings, 'EDUCATIONAL_SETTINGS', {}).get(
            'POINTS_PER_DIFFICULTY', 
            {1: 10, 2: 20, 3: 30, 4: 40, 5: 50}
        )
        return points_map.get(self.difficulty, 20)
    
    def mark_completed(self, score=None, feedback=""):
        """علامت‌گذاری تکلیف به عنوان تکمیل شده"""
        self.status = 'completed'
        self.completion_date = timezone.now()
        if score is not None:
            self.score = score
        if feedback:
            self.feedback = feedback
        self.save()
        
        # اضافه کردن امتیاز به دانش‌آموز
        points_earned = self.points_value
        if score and score >= 80:  # بونوس برای نمره بالا
            points_earned = int(points_earned * 1.2)
        
        result = self.student.add_points(points_earned, f"تکمیل تکلیف {self.title}")
        
        # به‌روزرسانی رکورد مطالعه
        self.student.update_study_streak()
        
        return result
    
    def get_grade_level(self):
        """دریافت پایه تحصیلی دانش‌آموز"""
        return self.student.grade_level
    
    def save(self, *args, **kwargs):
        """Override save برای به‌روزرسانی خودکار وضعیت"""
        # بررسی عقب‌افتادگی خودکار
        if (self.due_date < timezone.now() and 
            self.status == 'pending'):
            self.status = 'overdue'
        
        super().save(*args, **kwargs)


class HomeworkHelp(models.Model):
    """درخواست‌های کمک برای تکالیف"""
    homework = models.ForeignKey(
        Homework, 
        on_delete=models.CASCADE,
        related_name='help_requests'
    )
    question = models.TextField(verbose_name='سوال دانش‌آموز')
    ai_response = models.TextField(blank=True, verbose_name='پاسخ هوش مصنوعی')
    is_helpful = models.BooleanField(null=True, blank=True, verbose_name='مفید بود؟')
    additional_notes = models.TextField(blank=True, verbose_name='یادداشت اضافی')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'درخواست کمک'
        verbose_name_plural = 'درخواست‌های کمک'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"کمک برای {self.homework.title}"


class DailyActivity(models.Model):
    """فعالیت روزانه دانش‌آموز"""
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='daily_activities'
    )
    date = models.DateField(default=timezone.now)
    
    # آمار روزانه
    study_minutes = models.PositiveIntegerField(default=0)
    homeworks_completed = models.PositiveIntegerField(default=0)
    questions_asked = models.PositiveIntegerField(default=0)
    points_earned = models.PositiveIntegerField(default=0)
    
    # جزئیات فعالیت
    subjects_studied = models.JSONField(default=list)  # لیست ID دروس
    peak_activity_hour = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )
    
    class Meta:
        verbose_name = 'فعالیت روزانه'
        verbose_name_plural = 'فعالیت‌های روزانه'
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.date}"
    
    @classmethod
    def get_or_create_today(cls, student):
        """دریافت یا ایجاد فعالیت امروز"""
        today = timezone.now().date()
        activity, created = cls.objects.get_or_create(
            student=student,
            date=today,
            defaults={
                'study_minutes': 0,
                'homeworks_completed': 0,
                'questions_asked': 0,
                'points_earned': 0,
            }
        )
        return activity


# Signal handlers برای به‌روزرسانی خودکار
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    """ایجاد خودکار پروفایل دانش‌آموز برای کاربران جدید"""
    if created and not hasattr(instance, 'student_profile'):
        # فقط اگر کاربر کودک باشد (بر اساس username pattern یا سایر شرایط)
        # در حال حاضر برای همه کاربران ایجاد می‌شود
        pass  # پیاده‌سازی در فاز بعدی

@receiver(post_save, sender=Homework)
def update_homework_activity(sender, instance, created, **kwargs):
    """به‌روزرسانی فعالیت روزانه هنگام تغییر تکلیف"""
    if instance.status == 'completed' and instance.completion_date:
        activity = DailyActivity.get_or_create_today(instance.student)
        activity.homeworks_completed += 1
        activity.points_earned += instance.points_value
        activity.save()