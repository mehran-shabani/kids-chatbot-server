# Phase 2: Core Educational Features
## فاز 2: ویژگی‌های اصلی آموزشی (Agent Core)

**مدت پیاده‌سازی**: 3 هفته  
**Agent مسئول**: Core Agent  
**وابستگی**: Phase 1 Base باید کامل باشد

## اهداف فاز

### هدف اصلی
پیاده‌سازی ویژگی‌های اصلی آموزشی که چت‌بات را به یک دستیار واقعی تبدیل می‌کند

### اهداف فرعی
1. سیستم هوشمند تولید تکالیف
2. بانک سوال جامع با AI
3. سیستم گیمیفیکیشن کامل
4. یادآورهای هوشمند
5. تحلیل عملکرد تحصیلی

## ویژگی‌های جدید

### 1. AI Homework Assistant 🤖
- **تولید تکلیف هوشمند**: بر اساس نقاط ضعف
- **حل گام به گام**: توضیح مرحله‌ای مسائل
- **تصحیح خودکار**: بررسی پاسخ‌ها
- **پیشنهاد منابع**: کتاب و ویدیو مناسب

### 2. Question Bank System 📚
- **بانک سوال جامع**: 10,000+ سوال
- **دسته‌بندی هوشمند**: بر اساس موضوع و سختی
- **تولید خودکار**: AI برای سوالات جدید
- **ردیابی عملکرد**: آمار پاسخ‌ها

### 3. Advanced Gamification 🎮
- **سیستم مدال**: 50+ نوع دستاورد
- **لیدربورد**: رقابت سالم
- **چالش‌های روزانه**: انگیزه مداوم
- **آواتار و شخصی‌سازی**: هویت بصری

### 4. Smart Reminders ⏰
- **یادآور هوشمند**: بر اساس الگوی مطالعه
- **اعلانات تطبیقی**: زمان‌بندی بهینه
- **پیش‌بینی موعد**: هشدار زودهنگام
- **انگیزشی**: پیام‌های مثبت

## تحویل‌ها (Deliverables)

### 1. مدل‌های جدید
- [ ] Question model با AI integration
- [ ] Achievement و Badge system
- [ ] Reminder و Notification
- [ ] StudySession tracking
- [ ] QuizResult و Performance

### 2. AI Services
- [ ] Homework Generator Service
- [ ] Step-by-step Solver
- [ ] Content Recommender
- [ ] Performance Analyzer

### 3. Gamification System
- [ ] Points و Levels
- [ ] Badges و Achievements
- [ ] Leaderboard
- [ ] Daily Challenges

### 4. Notification System
- [ ] Smart Reminders
- [ ] Push Notifications
- [ ] Email Reports
- [ ] SMS Alerts

## Implementation Details

### AI Homework Assistant
```python
# educational/ai_services.py
class HomeworkAI:
    def generate_homework(self, subject, grade_level, difficulty, topic=None):
        """تولید تکلیف هوشمند"""
        prompt = f"""
        تولید تکلیف {subject.persian_name} برای پایه {grade_level}
        سطح سختی: {difficulty}/5
        {f'موضوع: {topic}' if topic else ''}
        
        خروجی به فرمت JSON:
        {{
            "title": "عنوان تکلیف",
            "description": "شرح کامل",
            "questions": [
                {{"question": "سوال 1", "answer": "پاسخ", "explanation": "توضیح"}},
                ...
            ],
            "estimated_minutes": 30,
            "learning_objectives": ["هدف 1", "هدف 2"]
        }}
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return json.loads(response.choices[0].message.content)
    
    def solve_step_by_step(self, question, grade_level):
        """حل گام به گام مسائل"""
        prompt = f"""
        سوال دانش‌آموز پایه {grade_level}:
        {question}
        
        لطفاً حل گام به گام ارائه دهید:
        1. درک مسئله
        2. شناسایی داده‌ها
        3. انتخاب روش حل
        4. محاسبه
        5. بررسی جواب
        
        زبان: فارسی ساده و کودکانه
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content
```

### Question Bank System
```python
# educational/models.py (اضافه به فاز 1)
class Question(models.Model):
    """بانک سوالات"""
    QUESTION_TYPES = [
        ('multiple_choice', 'چندگزینه‌ای'),
        ('true_false', 'درست/غلط'),
        ('short_answer', 'پاسخ کوتاه'),
        ('essay', 'تشریحی'),
        ('math_problem', 'مسئله ریاضی'),
        ('fill_blank', 'جای خالی'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade_level = models.PositiveSmallIntegerField()
    
    # محتوای سوال
    question_text = models.TextField(verbose_name='متن سوال')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # پاسخ‌ها
    correct_answer = models.TextField(verbose_name='پاسخ صحیح')
    explanation = models.TextField(verbose_name='توضیح')
    options = models.JSONField(default=dict, blank=True)  # برای چندگزینه‌ای
    
    # متادیتا
    tags = models.JSONField(default=list)  # موضوعات
    source = models.CharField(max_length=100, blank=True)  # منبع سوال
    created_by = models.CharField(max_length=20, default='AI')
    is_verified = models.BooleanField(default=False)
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)  # درصد پاسخ صحیح
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'سوال'
        verbose_name_plural = 'سوالات'
        indexes = [
            models.Index(fields=['subject', 'grade_level', 'difficulty']),
            models.Index(fields=['tags']),
        ]
    
    def __str__(self):
        return f"{self.question_text[:50]}..."

class QuizSession(models.Model):
    """جلسه آزمون/تمرین"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    questions = models.ManyToManyField(Question, through='QuizResult')
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    
    total_score = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'جلسه آزمون'
        verbose_name_plural = 'جلسات آزمون'

class QuizResult(models.Model):
    """نتیجه پاسخ به سوال"""
    quiz_session = models.ForeignKey(QuizSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    student_answer = models.TextField()
    is_correct = models.BooleanField()
    points_earned = models.FloatField(default=0.0)
    time_spent_seconds = models.PositiveIntegerField()
    
    answered_at = models.DateTimeField(auto_now_add=True)
```

### Gamification System
```python
# educational/models.py (ادامه)
class Achievement(models.Model):
    """دستاوردها و مدال‌ها"""
    CATEGORIES = [
        ('homework', 'تکالیف'),
        ('study_time', 'زمان مطالعه'),
        ('streak', 'تداوم'),
        ('subject_mastery', 'تسلط بر درس'),
        ('quiz_performance', 'عملکرد آزمون'),
        ('special', 'ویژه'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    persian_name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    # شرایط دریافت
    condition = models.JSONField(help_text="شرایط JSON برای دریافت مدال")
    points_reward = models.PositiveIntegerField(default=50)
    
    # نمایش
    icon = models.CharField(max_length=50, default='trophy')
    color = models.CharField(max_length=7, default='#ffd700')
    rarity = models.CharField(max_length=20, default='common')  # common/rare/epic/legendary
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def check_condition(self, student_profile):
        """بررسی شرایط دریافت مدال"""
        # پیاده‌سازی منطق بررسی شرایط
        pass

class StudentAchievement(models.Model):
    """دستاوردهای کسب شده دانش‌آموز"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    earned_at = models.DateTimeField(auto_now_add=True)
    progress_data = models.JSONField(default=dict)  # داده‌های پیشرفت
    
    class Meta:
        unique_together = ['student', 'achievement']
        verbose_name = 'دستاورد کسب شده'
        verbose_name_plural = 'دستاوردهای کسب شده'

class DailyChallenge(models.Model):
    """چالش‌های روزانه"""
    date = models.DateField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # شرایط چالش
    challenge_type = models.CharField(max_length=20)  # homework_count/study_time/quiz_score
    target_value = models.PositiveIntegerField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    grade_levels = models.JSONField(default=list)
    
    # پاداش
    points_reward = models.PositiveIntegerField(default=100)
    badge_reward = models.ForeignKey(Achievement, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'چالش روزانه'
        verbose_name_plural = 'چالش‌های روزانه'

class ChallengeParticipation(models.Model):
    """شرکت در چالش"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'challenge']
```

### Smart Reminders
```python
# educational/reminder_service.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import StudentProfile, Homework, DailyActivity

class SmartReminderService:
    """سرویس یادآورهای هوشمند"""
    
    @staticmethod
    def get_optimal_reminder_time(student_profile):
        """محاسبه بهترین زمان یادآوری"""
        # تحلیل الگوی مطالعه گذشته
        recent_activities = DailyActivity.objects.filter(
            student=student_profile,
            date__gte=timezone.now().date() - timedelta(days=7)
        )
        
        # یافتن ساعت فعالیت بیشتر
        peak_hours = []
        for activity in recent_activities:
            if activity.peak_activity_hour:
                peak_hours.append(activity.peak_activity_hour)
        
        if peak_hours:
            optimal_hour = max(set(peak_hours), key=peak_hours.count)
        else:
            optimal_hour = 16  # 4 عصر پیش‌فرض
        
        return optimal_hour
    
    @shared_task
    def send_homework_reminders():
        """ارسال یادآور تکالیف"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # تکالیف فردا
        upcoming_homeworks = Homework.objects.filter(
            due_date__date=tomorrow,
            status__in=['pending', 'in_progress']
        ).select_related('student', 'subject')
        
        for homework in upcoming_homeworks:
            student = homework.student
            
            # بررسی تنظیمات اعلان
            if not student.notification_homework:
                continue
            
            # ارسال اعلان
            message = f"""
            🔔 یادآور تکلیف
            
            درس: {homework.subject.persian_name}
            عنوان: {homework.title}
            موعد: فردا
            زمان تخمینی: {homework.estimated_minutes} دقیقه
            
            بیا شروع کنیم! 💪
            """
            
            # ارسال از طریق کانال‌های مختلف
            NotificationService.send_push(student.user, message)
            
            # SMS برای موارد مهم
            if homework.priority >= 4:
                NotificationService.send_sms(student.user.phone_number, message)
    
    @shared_task
    def send_daily_motivation():
        """ارسال انگیزه روزانه"""
        active_students = StudentProfile.objects.filter(
            last_activity_date__gte=timezone.now().date() - timedelta(days=3),
            notification_daily_reminder=True
        )
        
        for student in active_students:
            optimal_time = SmartReminderService.get_optimal_reminder_time(student)
            current_hour = timezone.now().hour
            
            # ارسال در زمان بهینه
            if current_hour == optimal_time:
                motivation_message = MotivationGenerator.get_daily_message(student)
                NotificationService.send_push(student.user, motivation_message)

class MotivationGenerator:
    """تولید پیام‌های انگیزشی"""
    
    MESSAGES = {
        'streak': [
            "🔥 {streak} روز متوالی! رکوردت فوق‌العاده است!",
            "💪 {streak} روز پشت سر هم! ادامه بده قهرمان!",
            "⭐ {streak} روز بدون وقفه! تو واقعاً عالی هستی!"
        ],
        'homework': [
            "📚 {count} تکلیف امروز داری. بیا شروع کنیم!",
            "✏️ وقت انجام تکالیف! {count} تا منتظرت هستند.",
            "🎯 {count} تکلیف، {count} فرصت برای یادگیری!"
        ],
        'level_up': [
            "🎉 تبریک! به سطح {level} رسیدی!",
            "🚀 سطح جدید! حالا سطح {level} هستی!",
            "👑 ارتقا یافتی! سطح {level} منتظرت بود!"
        ]
    }
    
    @classmethod
    def get_daily_message(cls, student_profile):
        """تولید پیام روزانه"""
        import random
        
        # انتخاب نوع پیام بر اساس وضعیت
        if student_profile.study_streak >= 3:
            messages = cls.MESSAGES['streak']
            return random.choice(messages).format(streak=student_profile.study_streak)
        
        # بررسی تکالیف امروز
        today_homeworks = student_profile.homeworks.filter(
            due_date__date=timezone.now().date(),
            status__in=['pending', 'in_progress']
        ).count()
        
        if today_homeworks > 0:
            messages = cls.MESSAGES['homework']
            return random.choice(messages).format(count=today_homeworks)
        
        # پیام عمومی
        general_messages = [
            "🌟 امروز روز خوبی برای یادگیری است!",
            "📖 آماده‌ای برای کشف چیزهای جدید؟",
            "💡 هر روز قدمی به جلو! بیا شروع کنیم!"
        ]
        
        return random.choice(general_messages)
```

### Performance Analytics
```python
# educational/analytics.py
class PerformanceAnalyzer:
    """تحلیل‌گر عملکرد تحصیلی"""
    
    def __init__(self, student_profile):
        self.student = student_profile
    
    def get_subject_performance(self, days=30):
        """تحلیل عملکرد در هر درس"""
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        homeworks = self.student.homeworks.filter(
            assigned_date__date__gte=cutoff_date,
            status='completed'
        ).select_related('subject')
        
        subject_stats = {}
        for homework in homeworks:
            subject_name = homework.subject.persian_name
            
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {
                    'total_homeworks': 0,
                    'total_score': 0,
                    'total_time': 0,
                    'difficulties': []
                }
            
            stats = subject_stats[subject_name]
            stats['total_homeworks'] += 1
            if homework.score:
                stats['total_score'] += homework.score
            stats['total_time'] += homework.estimated_minutes
            stats['difficulties'].append(homework.difficulty)
        
        # محاسبه میانگین‌ها
        for subject, stats in subject_stats.items():
            if stats['total_homeworks'] > 0:
                stats['average_score'] = stats['total_score'] / stats['total_homeworks']
                stats['average_difficulty'] = sum(stats['difficulties']) / len(stats['difficulties'])
            else:
                stats['average_score'] = 0
                stats['average_difficulty'] = 0
        
        return subject_stats
    
    def identify_weak_areas(self):
        """شناسایی نقاط ضعف"""
        performance = self.get_subject_performance()
        
        weak_subjects = []
        for subject, stats in performance.items():
            if stats['average_score'] < 70:  # کمتر از 70
                weak_subjects.append({
                    'subject': subject,
                    'average_score': stats['average_score'],
                    'recommendation': self._get_improvement_recommendation(subject, stats)
                })
        
        return sorted(weak_subjects, key=lambda x: x['average_score'])
    
    def _get_improvement_recommendation(self, subject, stats):
        """پیشنهاد بهبود"""
        if stats['average_score'] < 50:
            return f"نیاز به تمرین بیشتر در {subject}. پیشنهاد: تمرین روزانه 15 دقیقه"
        elif stats['average_score'] < 70:
            return f"عملکرد قابل قبول در {subject}. پیشنهاد: مرور مباحث ضعیف"
        else:
            return f"عملکرد خوب در {subject}. ادامه بده!"
    
    def generate_study_plan(self, days=7):
        """تولید برنامه مطالعه"""
        weak_areas = self.identify_weak_areas()
        daily_goal = self.student.daily_study_goal
        
        plan = {}
        for i in range(days):
            date = timezone.now().date() + timedelta(days=i)
            
            # تقسیم زمان بین دروس ضعیف
            if weak_areas:
                time_per_subject = daily_goal // len(weak_areas)
                daily_plan = []
                
                for weak_area in weak_areas:
                    daily_plan.append({
                        'subject': weak_area['subject'],
                        'minutes': time_per_subject,
                        'focus': 'تقویت نقاط ضعف'
                    })
                
                plan[date.isoformat()] = daily_plan
            else:
                # برنامه متعادل
                plan[date.isoformat()] = [{
                    'subject': 'مرور کلی',
                    'minutes': daily_goal,
                    'focus': 'حفظ سطح فعلی'
                }]
        
        return plan
```

### API Views برای فاز 2
```python
# educational/views.py (ادامه فاز 1)

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای بانک سوالات"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            grade = self.request.user.student_profile.grade_level
            return Question.objects.filter(
                grade_level=grade,
                is_verified=True
            ).select_related('subject')
        return Question.objects.none()
    
    @action(detail=False, methods=['post'])
    def generate_quiz(self, request):
        """تولید آزمون"""
        subject_id = request.data.get('subject_id')
        difficulty = request.data.get('difficulty', 2)
        question_count = request.data.get('count', 10)
        
        questions = self.get_queryset().filter(
            subject_id=subject_id,
            difficulty=difficulty
        ).order_by('?')[:question_count]  # انتخاب تصادفی
        
        # ایجاد جلسه آزمون
        quiz_session = QuizSession.objects.create(
            student=request.user.student_profile,
            subject_id=subject_id,
            title=f"آزمون {questions.first().subject.persian_name}"
        )
        
        quiz_session.questions.set(questions)
        
        return Response({
            'quiz_session_id': quiz_session.id,
            'questions': QuestionSerializer(questions, many=True).data
        })

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای دستاوردها"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Achievement.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        """دستاوردهای کسب شده کاربر"""
        if not hasattr(request.user, 'student_profile'):
            return Response({'achievements': []})
        
        earned = StudentAchievement.objects.filter(
            student=request.user.student_profile
        ).select_related('achievement')
        
        return Response({
            'earned_count': earned.count(),
            'achievements': [
                {
                    'achievement': AchievementSerializer(sa.achievement).data,
                    'earned_at': sa.earned_at,
                    'progress_data': sa.progress_data
                }
                for sa in earned
            ]
        })
    
    @action(detail=False, methods=['post'])
    def check_new_achievements(self, request):
        """بررسی دستاوردهای جدید"""
        if not hasattr(request.user, 'student_profile'):
            return Response({'new_achievements': []})
        
        student = request.user.student_profile
        new_achievements = []
        
        # بررسی شرایط دستاوردها
        for achievement in Achievement.objects.filter(is_active=True):
            if not StudentAchievement.objects.filter(
                student=student, 
                achievement=achievement
            ).exists():
                if self._check_achievement_condition(student, achievement):
                    # اعطای دستاورد
                    StudentAchievement.objects.create(
                        student=student,
                        achievement=achievement
                    )
                    
                    # اضافه کردن امتیاز
                    student.add_points(achievement.points_reward, f"دستاورد: {achievement.persian_name}")
                    
                    new_achievements.append(achievement)
        
        return Response({
            'new_achievements': AchievementSerializer(new_achievements, many=True).data,
            'message': f"{len(new_achievements)} دستاورد جدید کسب کردی!" if new_achievements else "فعلاً دستاورد جدیدی نداری"
        })
    
    def _check_achievement_condition(self, student, achievement):
        """بررسی شرایط دستاورد"""
        condition = achievement.condition
        
        if achievement.category == 'homework':
            completed_count = student.homeworks.filter(status='completed').count()
            return completed_count >= condition.get('min_homeworks', 10)
        
        elif achievement.category == 'streak':
            return student.study_streak >= condition.get('min_days', 7)
        
        elif achievement.category == 'study_time':
            total_minutes = sum(
                a.study_minutes for a in student.daily_activities.all()
            )
            return total_minutes >= condition.get('min_minutes', 600)
        
        return False
```

## Testing Strategy فاز 2

### Test Coverage Requirements
- [ ] Unit Tests: 85%+
- [ ] Integration Tests: کلیه API endpoints
- [ ] Performance Tests: زمان پاسخ < 2 ثانیه
- [ ] Security Tests: دسترسی و validation

### Sample Tests
```python
# educational/tests/test_ai_services.py
class AIHomeworkTest(TestCase):
    def test_homework_generation(self):
        """تست تولید تکلیف با AI"""
        ai_service = HomeworkAI()
        
        subject = Subject.objects.create(name='math', persian_name='ریاضی')
        result = ai_service.generate_homework(subject, 5, 2)
        
        self.assertIn('title', result)
        self.assertIn('questions', result)
        self.assertIsInstance(result['questions'], list)
        self.assertGreater(len(result['questions']), 0)

# educational/tests/test_gamification.py  
class GamificationTest(TestCase):
    def test_achievement_system(self):
        """تست سیستم دستاوردها"""
        # تست منطق اعطای مدال
        pass
```

## Deployment Notes

### Environment Variables
```bash
# .env اضافه کنید:
OPENAI_API_KEY=your_openai_key
EDUCATIONAL_MODE=true
AI_SAFETY_LEVEL=high
CONTENT_FILTER_ENABLED=true
GAMIFICATION_ENABLED=true
```

### Database Migrations
```bash
# اجرای migrations جدید
python manage.py makemigrations educational
python manage.py migrate

# راه‌اندازی داده‌های پایه
python manage.py setup_educational_data
python manage.py setup_achievements
python manage.py setup_question_bank
```

## Success Metrics

### Technical KPIs
- [ ] API Response Time < 2s
- [ ] AI Response Accuracy > 90%
- [ ] Question Bank > 5,000 items
- [ ] Achievement System 20+ badges

### User Experience KPIs  
- [ ] Homework Completion Rate > 75%
- [ ] Daily Active Users retention > 60%
- [ ] Average Session Time > 15 minutes
- [ ] User Satisfaction Score > 4.5/5

### Educational KPIs
- [ ] Grade Improvement > 10%
- [ ] Study Time Increase > 25%
- [ ] Parent Satisfaction > 80%
- [ ] Teacher Approval > 70%

---

**نکته**: این فاز بر پایه فاز 1 ساخته می‌شود و ویژگی‌های اصلی آموزشی را اضافه می‌کند.