# Phase 1: Base Educational Foundation
## فاز 1: پایه‌گذاری آموزشی (Agent Base)

**مدت پیاده‌سازی**: 2 هفته  
**Agent مسئول**: Base Agent  
**اولویت**: بسیار بالا

## اهداف فاز

### هدف اصلی
ایجاد زیرساخت پایه‌ای برای تبدیل چت‌بات عمومی به سیستم آموزشی تخصصی کودکان

### اهداف فرعی
1. گسترش مدل User برای دانش‌آموزان
2. ایجاد ساختار دروس و پایه‌های تحصیلی
3. پایه‌گذاری سیستم تکالیف
4. تنظیم API‌های پایه

## تحویل‌ها (Deliverables)

### 1. مدل‌های دیتابیس جدید
- [ ] StudentProfile model
- [ ] Subject model  
- [ ] Grade model
- [ ] Homework model (ساده)

### 2. Migration‌ها
- [ ] Migration برای گسترش User
- [ ] Migration برای ایجاد جداول آموزشی
- [ ] Data seeding برای دروس پایه

### 3. API‌های پایه
- [ ] Student profile CRUD
- [ ] Subject list API
- [ ] Basic homework API

### 4. تست‌ها
- [ ] Unit tests برای مدل‌ها
- [ ] API tests
- [ ] Integration tests

## پیش‌نیازها

### فنی
- Django 4.2+ نصب شده
- PostgreSQL در حال اجرا
- Redis برای caching
- Environment variables تنظیم شده

### دانش مورد نیاز
- Django ORM و migrations
- Django REST Framework
- PostgreSQL و SQL
- Git workflow

## Implementation Guide

### گام 1: ایجاد Educational App
```bash
# در پوشه پروژه
python manage.py startapp educational
```

### گام 2: تعریف مدل‌ها
```python
# educational/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Subject(models.Model):
    """دروس تحصیلی"""
    name = models.CharField(max_length=50, unique=True)
    persian_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, default='#007bff')
    icon = models.CharField(max_length=50, default='book')
    grade_levels = models.JSONField(default=list)  # [1,2,3,...]
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'دروس'
    
    def __str__(self):
        return self.persian_name

class StudentProfile(models.Model):
    """پروفایل تحصیلی دانش‌آموز"""
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
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    
    # اطلاعات تحصیلی
    grade_level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPES, default='public')
    school_name = models.CharField(max_length=200, blank=True)
    
    # اطلاعات شخصی
    birth_date = models.DateField(null=True, blank=True)
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLES, default='visual')
    
    # تنظیمات مطالعه
    daily_study_goal = models.PositiveIntegerField(default=60)  # دقیقه
    preferred_subjects = models.ManyToManyField(Subject, blank=True)
    
    # گیمیفیکیشن پایه
    total_points = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    study_streak = models.PositiveIntegerField(default=0)
    
    # UI/UX
    avatar_url = models.URLField(blank=True)
    theme_preference = models.CharField(max_length=20, default='default')
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'دانش‌آموز'
        verbose_name_plural = 'دانش‌آموزان'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - پایه {self.grade_level}"
    
    @property
    def age(self):
        if self.birth_date:
            from datetime import date
            return (date.today() - self.birth_date).days // 365
        return None

class Homework(models.Model):
    """تکالیف دانش‌آموزان"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('completed', 'تکمیل شده'),
        ('overdue', 'گذشته از موعد'),
        ('reviewed', 'بررسی شده'),
    ]
    
    DIFFICULTY_CHOICES = [
        (1, 'آسان'),
        (2, 'متوسط'),
        (3, 'سخت'),
        (4, 'خیلی سخت'),
        (5, 'چالشی'),
    ]
    
    student = models.ForeignKey(
        StudentProfile, 
        on_delete=models.CASCADE,
        related_name='homeworks'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # محتوای تکلیف
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(blank=True)
    
    # زمان‌بندی
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    estimated_minutes = models.PositiveIntegerField(default=30)
    
    # ویژگی‌ها
    difficulty = models.PositiveSmallIntegerField(choices=DIFFICULTY_CHOICES, default=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # نتایج
    completion_date = models.DateTimeField(null=True, blank=True)
    score = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    feedback = models.TextField(blank=True)
    
    # فایل‌ها
    attachment_url = models.URLField(blank=True)
    submission_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'تکلیف'
        verbose_name_plural = 'تکالیف'
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now() and self.status != 'completed'
```

### گام 3: Serializers
```python
# educational/serializers.py
from rest_framework import serializers
from .models import StudentProfile, Subject, Homework

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'persian_name', 'description', 'color_code', 'icon']

class StudentProfileSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    preferred_subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'grade_level', 'school_type', 'school_name', 'birth_date',
            'learning_style', 'daily_study_goal', 'total_points',
            'current_level', 'study_streak', 'avatar_url', 
            'theme_preference', 'age', 'preferred_subjects'
        ]
    
    def validate_grade_level(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("پایه تحصیلی باید بین 1 تا 12 باشد")
        return value

class HomeworkSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.persian_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Homework
        fields = [
            'id', 'title', 'description', 'subject', 'subject_name',
            'due_date', 'estimated_minutes', 'difficulty', 'status',
            'score', 'feedback', 'is_overdue', 'assigned_date'
        ]
        read_only_fields = ['assigned_date', 'student']

class HomeworkCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homework
        fields = ['title', 'description', 'subject', 'due_date', 'estimated_minutes', 'difficulty']
```

### گام 4: Views و API‌ها
```python
# educational/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import StudentProfile, Subject, Homework
from .serializers import StudentProfileSerializer, SubjectSerializer, HomeworkSerializer

class StudentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StudentProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """داشبورد اصلی دانش‌آموز"""
        profile = self.get_object()
        
        # آمار کلی
        total_homeworks = profile.homeworks.count()
        completed_homeworks = profile.homeworks.filter(status='completed').count()
        pending_homeworks = profile.homeworks.filter(status='pending').count()
        
        # تکالیف امروز
        from django.utils import timezone
        today = timezone.now().date()
        today_homeworks = profile.homeworks.filter(
            due_date__date=today
        ).values('title', 'subject__persian_name', 'difficulty')
        
        return Response({
            'profile': StudentProfileSerializer(profile).data,
            'stats': {
                'total_homeworks': total_homeworks,
                'completed_homeworks': completed_homeworks,
                'pending_homeworks': pending_homeworks,
                'completion_rate': round((completed_homeworks / total_homeworks * 100) if total_homeworks > 0 else 0, 1)
            },
            'today_homeworks': list(today_homeworks),
            'current_streak': profile.study_streak,
            'next_level_points': (profile.current_level * 100) - profile.total_points
        })

class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # فیلتر بر اساس پایه تحصیلی دانش‌آموز
        if hasattr(self.request.user, 'student_profile'):
            grade = self.request.user.student_profile.grade_level
            return self.queryset.filter(grade_levels__contains=[grade])
        return self.queryset

class HomeworkViewSet(viewsets.ModelViewSet):
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return Homework.objects.filter(student=self.request.user.student_profile)
        return Homework.objects.none()
    
    def perform_create(self, serializer):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        serializer.save(student=student_profile)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """تکالیف امروز"""
        from django.utils import timezone
        today = timezone.now().date()
        
        homeworks = self.get_queryset().filter(
            due_date__date=today,
            status__in=['pending', 'in_progress']
        )
        
        serializer = self.get_serializer(homeworks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """تکالیف عقب‌افتاده"""
        from django.utils import timezone
        now = timezone.now()
        
        homeworks = self.get_queryset().filter(
            due_date__lt=now,
            status__in=['pending', 'in_progress']
        )
        
        serializer = self.get_serializer(homeworks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """علامت‌گذاری تکلیف به عنوان تکمیل شده"""
        homework = self.get_object()
        homework.status = 'completed'
        homework.completion_date = timezone.now()
        homework.save()
        
        # اضافه کردن امتیاز به دانش‌آموز
        student = homework.student
        points = homework.difficulty * 10  # 10-50 امتیاز
        student.total_points += points
        student.save()
        
        return Response({
            'message': 'تکلیف با موفقیت تکمیل شد!',
            'points_earned': points,
            'total_points': student.total_points
        })
```

### گام 3: URL Configuration
```python
# educational/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentProfileViewSet, SubjectViewSet, HomeworkViewSet

router = DefaultRouter()
router.register(r'profiles', StudentProfileViewSet, basename='student-profile')
router.register(r'subjects', SubjectViewSet)
router.register(r'homeworks', HomeworkViewSet, basename='homework')

urlpatterns = [
    path('api/educational/', include(router.urls)),
]
```

### گام 4: Settings Updates
```python
# در config/settings.py اضافه کنید:
INSTALLED_APPS += [
    'educational',
]

# تنظیمات آموزشی
EDUCATIONAL_SETTINGS = {
    'GRADE_LEVELS': {
        1: 'اول ابتدایی', 2: 'دوم ابتدایی', 3: 'سوم ابتدایی',
        4: 'چهارم ابتدایی', 5: 'پنجم ابتدایی', 6: 'ششم ابتدایی',
        7: 'اول متوسطه', 8: 'دوم متوسطه', 9: 'سوم متوسطه',
        10: 'اول دبیرستان', 11: 'دوم دبیرستان', 12: 'سوم دبیرستان',
    },
    'DEFAULT_SUBJECTS': [
        {'name': 'math', 'persian_name': 'ریاضی', 'color': '#e74c3c'},
        {'name': 'science', 'persian_name': 'علوم', 'color': '#2ecc71'},
        {'name': 'persian', 'persian_name': 'فارسی', 'color': '#3498db'},
        {'name': 'social', 'persian_name': 'اجتماعی', 'color': '#f39c12'},
        {'name': 'english', 'persian_name': 'انگلیسی', 'color': '#9b59b6'},
    ],
    'POINTS_PER_DIFFICULTY': {1: 10, 2: 20, 3: 30, 4: 40, 5: 50},
    'LEVEL_UP_POINTS': 100,  # امتیاز لازم برای سطح بعدی
}
```

### گام 5: Management Commands
```python
# educational/management/commands/setup_educational_data.py
from django.core.management.base import BaseCommand
from django.conf import settings
from educational.models import Subject

class Command(BaseCommand):
    help = 'راه‌اندازی داده‌های پایه آموزشی'
    
    def handle(self, *args, **options):
        # ایجاد دروس پایه
        subjects_data = settings.EDUCATIONAL_SETTINGS['DEFAULT_SUBJECTS']
        
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                name=subject_data['name'],
                defaults={
                    'persian_name': subject_data['persian_name'],
                    'color_code': subject_data['color'],
                    'grade_levels': list(range(1, 13)),  # همه پایه‌ها
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'درس {subject.persian_name} ایجاد شد')
                )
            else:
                self.stdout.write(f'درس {subject.persian_name} قبلاً وجود داشت')
        
        self.stdout.write(
            self.style.SUCCESS('راه‌اندازی داده‌های آموزشی با موفقیت انجام شد')
        )
```

### گام 6: Tests
```python
# educational/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import StudentProfile, Subject, Homework

User = get_user_model()

class StudentProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
    
    def test_create_student_profile(self):
        profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5,
            school_type='public',
            daily_study_goal=90
        )
        
        self.assertEqual(profile.grade_level, 5)
        self.assertEqual(profile.total_points, 0)
        self.assertEqual(profile.current_level, 1)

class HomeworkAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5
        )
        self.subject = Subject.objects.create(
            name='math',
            persian_name='ریاضی'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_homework(self):
        url = reverse('homework-list')
        data = {
            'title': 'تمرین ضرب',
            'description': 'حل مسائل صفحه 25',
            'subject': self.subject.id,
            'due_date': '2024-01-20T18:00:00Z',
            'difficulty': 2
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Homework.objects.count(), 1)
    
    def test_mark_homework_complete(self):
        homework = Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تست',
            description='تست',
            due_date='2024-01-20T18:00:00Z',
            difficulty=3
        )
        
        url = reverse('homework-mark-complete', kwargs={'pk': homework.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        homework.refresh_from_db()
        self.assertEqual(homework.status, 'completed')
        
        # بررسی امتیاز
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_points, 30)  # 3 * 10
```

## دستورات اجرا

### 1. راه‌اندازی
```bash
# اضافه کردن app به settings
# ایجاد migrations
python manage.py makemigrations educational
python manage.py migrate

# راه‌اندازی داده‌های پایه
python manage.py setup_educational_data

# تست
python manage.py test educational
```

### 2. تست API‌ها
```bash
# دریافت لیست دروس
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/educational/subjects/

# ایجاد پروفایل دانش‌آموز
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"grade_level": 5, "school_type": "public", "daily_study_goal": 60}' \
     http://localhost:8000/api/educational/profiles/

# داشبورد دانش‌آموز
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/educational/profiles/1/dashboard/
```

## معیارهای تایید فاز

### تست‌های لازم
- [ ] همه Unit tests پاس شوند
- [ ] API endpoints کار کنند
- [ ] Migration بدون خطا اجرا شود
- [ ] داده‌های seed درست لود شوند

### عملکرد مورد انتظار
- [ ] ایجاد پروفایل دانش‌آموز < 1 ثانیه
- [ ] لیست تکالیف < 500ms
- [ ] داشبورد کامل < 2 ثانیه

### کیفیت کد
- [ ] Test coverage > 80%
- [ ] Type hints برای همه functions
- [ ] Docstrings برای کلاس‌ها
- [ ] PEP8 compliance

## مستندات API

### Endpoints اضافه شده
```
POST   /api/educational/profiles/           # ایجاد پروفایل
GET    /api/educational/profiles/{id}/      # دریافت پروفایل
PUT    /api/educational/profiles/{id}/      # به‌روزرسانی پروفایل
GET    /api/educational/profiles/{id}/dashboard/  # داشبورد

GET    /api/educational/subjects/           # لیست دروس

POST   /api/educational/homeworks/          # ایجاد تکلیف
GET    /api/educational/homeworks/          # لیست تکالیف
GET    /api/educational/homeworks/today/    # تکالیف امروز
GET    /api/educational/homeworks/overdue/  # تکالیف عقب‌افتاده
POST   /api/educational/homeworks/{id}/mark_complete/  # تکمیل تکلیف
```

---

**نکته مهم**: این فاز پایه‌ای است و فقط ساختار اصلی را فراهم می‌کند. ویژگی‌های پیشرفته در فازهای بعدی اضافه خواهند شد.