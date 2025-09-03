# Phase 3: Parental Control & Monitoring
## فاز 3: کنترل والدین و نظارت (Agent Parent)

**مدت پیاده‌سازی**: 2 هفته  
**Agent مسئول**: Parent Agent  
**وابستگی**: Phase 1 Base + Phase 2 Core

## اهداف فاز

### هدف اصلی
ایجاد سیستم جامع کنترل والدین و نظارت بر فعالیت‌های آموزشی فرزندان

### اهداف فرعی
1. داشبورد والدین
2. سیستم گزارش‌دهی
3. کنترل زمان و محتوا
4. اعلانات والدین
5. تنظیمات ایمنی

## ویژگی‌های جدید

### 1. Parent Dashboard 👨‍👩‍👧‍👦
- **نمای کلی عملکرد**: آمار هفتگی/ماهانه
- **پیشرفت تحصیلی**: نمودارها و ترندها
- **فعالیت‌های اخیر**: timeline کامل
- **هشدارهای مهم**: نقاط نگران‌کننده

### 2. Time Management ⏰
- **محدودیت زمانی**: ساعات مجاز استفاده
- **کنترل روزانه**: حداکثر زمان در روز
- **برنامه هفتگی**: تنظیم برنامه مطالعه
- **استراحت اجباری**: فاصله بین جلسات

### 3. Content Control 🛡️
- **فیلتر محتوا**: سطوح مختلف فیلترینگ
- **موضوعات مجاز**: انتخاب دروس قابل دسترس
- **کنترل AI**: نظارت بر پاسخ‌های هوش مصنوعی
- **بلاک لیست**: کلمات و موضوعات ممنوع

### 4. Reporting System 📊
- **گزارش هفتگی**: ایمیل/SMS خودکار
- **آمار تفصیلی**: عمق عملکرد
- **مقایسه با میانگین**: بنچمارک کلاسی
- **پیشنهادات بهبود**: راهکارهای عملی

## Models جدید

### Parent Profile
```python
# educational/models.py (اضافه شود)
class ParentProfile(models.Model):
    """پروفایل والدین"""
    RELATIONSHIP_CHOICES = [
        ('father', 'پدر'),
        ('mother', 'مادر'),
        ('guardian', 'سرپرست'),
        ('grandparent', 'پدربزرگ/مادربزرگ'),
        ('other', 'سایر'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    
    # اطلاعات شخصی
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    children = models.ManyToManyField(
        StudentProfile,
        related_name='parents',
        verbose_name='فرزندان'
    )
    
    # تنظیمات اعلانات
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    weekly_report = models.BooleanField(default=True)
    emergency_alerts = models.BooleanField(default=True)
    
    # ترجیحات گزارش‌دهی
    report_frequency = models.CharField(
        max_length=20,
        choices=[('daily', 'روزانه'), ('weekly', 'هفتگی'), ('monthly', 'ماهانه')],
        default='weekly'
    )
    report_time = models.TimeField(default='20:00')  # ساعت ارسال گزارش
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'پروفایل والدین'
        verbose_name_plural = 'پروفایل‌های والدین'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_relationship_display()})"

class ParentalControl(models.Model):
    """تنظیمات کنترل والدین"""
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='parental_control'
    )
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    
    # کنترل زمان
    daily_time_limit = models.PositiveIntegerField(
        default=120,  # 2 ساعت
        help_text="حداکثر زمان استفاده روزانه (دقیقه)"
    )
    allowed_start_time = models.TimeField(default='07:00')
    allowed_end_time = models.TimeField(default='21:00')
    weekend_time_limit = models.PositiveIntegerField(default=180)  # 3 ساعت
    
    # روزهای مجاز (0=دوشنبه، 6=یکشنبه)
    allowed_weekdays = models.JSONField(default=lambda: [0,1,2,3,4,5,6])
    
    # کنترل محتوا
    content_filter_level = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=آزاد، 5=خیلی سخت"
    )
    allowed_subjects = models.ManyToManyField(Subject, blank=True)
    blocked_keywords = models.JSONField(default=list)
    
    # کنترل AI
    ai_supervision = models.BooleanField(default=True, help_text="نظارت بر پاسخ‌های AI")
    require_parent_approval = models.BooleanField(
        default=False, 
        help_text="تایید والدین برای سوالات خاص"
    )
    
    # تنظیمات هشدار
    homework_deadline_alert = models.PositiveIntegerField(
        default=24,
        help_text="هشدار قبل از موعد تکلیف (ساعت)"
    )
    low_performance_alert = models.BooleanField(default=True)
    excessive_usage_alert = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'کنترل والدین'
        verbose_name_plural = 'کنترل‌های والدین'

class ParentNotification(models.Model):
    """اعلانات والدین"""
    NOTIFICATION_TYPES = [
        ('homework_completed', 'تکلیف تکمیل شد'),
        ('homework_overdue', 'تکلیف عقب‌افتاده'),
        ('achievement_earned', 'دستاورد جدید'),
        ('low_performance', 'عملکرد پایین'),
        ('excessive_usage', 'استفاده بیش از حد'),
        ('weekly_report', 'گزارش هفتگی'),
        ('system_alert', 'هشدار سیستم'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('urgent', 'فوری'),
    ]
    
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)  # داده‌های اضافی
    
    # وضعیت ارسال
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # کانال‌های ارسال
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    sent_via_push = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'اعلان والدین'
        verbose_name_plural = 'اعلانات والدین'
        ordering = ['-created_at']

class UsageSession(models.Model):
    """جلسات استفاده سیستم"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    
    # فعالیت‌های جلسه
    homeworks_worked = models.PositiveIntegerField(default=0)
    questions_asked = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    
    # دستگاه و مکان
    device_type = models.CharField(max_length=20, blank=True)  # mobile/tablet/desktop
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'جلسه استفاده'
        verbose_name_plural = 'جلسات استفاده'
```

## API Views

### Parent Dashboard API
```python
# educational/views.py (اضافه شود)
class ParentViewSet(viewsets.ModelViewSet):
    """API برای والدین"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ParentProfile.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """داشبورد والدین"""
        parent = self.get_object()
        children_data = []
        
        for child in parent.children.all():
            # آمار هفته جاری
            week_start = timezone.now().date() - timedelta(days=7)
            week_homeworks = child.homeworks.filter(
                assigned_date__date__gte=week_start
            )
            
            # فعالیت‌های هفته
            week_activities = child.daily_activities.filter(
                date__gte=week_start
            )
            
            total_study_time = sum(a.study_minutes for a in week_activities)
            completed_homeworks = week_homeworks.filter(status='completed').count()
            total_homeworks = week_homeworks.count()
            
            # نقاط قوت و ضعف
            analyzer = PerformanceAnalyzer(child)
            weak_areas = analyzer.identify_weak_areas()
            
            children_data.append({
                'child': StudentProfileSerializer(child).data,
                'weekly_stats': {
                    'study_minutes': total_study_time,
                    'homeworks_completed': completed_homeworks,
                    'homeworks_total': total_homeworks,
                    'completion_rate': round(
                        (completed_homeworks / total_homeworks * 100) if total_homeworks > 0 else 0, 1
                    ),
                    'average_score': week_homeworks.filter(
                        status='completed', score__isnull=False
                    ).aggregate(avg=models.Avg('score'))['avg'] or 0
                },
                'concerns': weak_areas[:2],  # دو نقطه ضعف اصلی
                'achievements_this_week': child.studentachievement_set.filter(
                    earned_at__gte=timezone.now() - timedelta(days=7)
                ).count()
            })
        
        return Response({
            'parent': ParentProfileSerializer(parent).data,
            'children': children_data,
            'summary': {
                'total_children': len(children_data),
                'active_children': len([c for c in children_data if c['weekly_stats']['study_minutes'] > 0]),
                'total_study_hours': sum(c['weekly_stats']['study_minutes'] for c in children_data) / 60,
                'average_completion_rate': sum(c['weekly_stats']['completion_rate'] for c in children_data) / len(children_data) if children_data else 0
            }
        })
    
    @action(detail=True, methods=['get'])
    def detailed_report(self, request, pk=None):
        """گزارش تفصیلی فرزند مشخص"""
        parent = self.get_object()
        child_id = request.query_params.get('child_id')
        
        if not child_id:
            return Response(
                {'error': 'child_id الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            child = parent.children.get(id=child_id)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'فرزند یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # گزارش 30 روز گذشته
        days = int(request.query_params.get('days', 30))
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        # فعالیت‌های روزانه
        daily_activities = child.daily_activities.filter(
            date__gte=cutoff_date
        ).order_by('date')
        
        # تکالیف
        homeworks = child.homeworks.filter(
            assigned_date__date__gte=cutoff_date
        ).select_related('subject')
        
        # آمار کلی
        total_study_minutes = sum(a.study_minutes for a in daily_activities)
        completed_homeworks = homeworks.filter(status='completed').count()
        average_score = homeworks.filter(
            status='completed', score__isnull=False
        ).aggregate(avg=models.Avg('score'))['avg'] or 0
        
        # تحلیل عملکرد
        analyzer = PerformanceAnalyzer(child)
        subject_performance = analyzer.get_subject_performance(days)
        study_plan = analyzer.generate_study_plan()
        
        return Response({
            'child': StudentProfileSerializer(child).data,
            'period': {
                'start_date': cutoff_date,
                'end_date': timezone.now().date(),
                'days': days
            },
            'summary': {
                'total_study_minutes': total_study_minutes,
                'average_daily_minutes': round(total_study_minutes / days, 1),
                'completed_homeworks': completed_homeworks,
                'total_homeworks': homeworks.count(),
                'completion_rate': round((completed_homeworks / homeworks.count() * 100) if homeworks.count() > 0 else 0, 1),
                'average_score': round(average_score, 1),
                'current_streak': child.study_streak
            },
            'daily_activities': DailyActivitySerializer(daily_activities, many=True).data,
            'subject_performance': subject_performance,
            'recommended_study_plan': study_plan,
            'concerns': analyzer.identify_weak_areas()
        })
    
    @action(detail=True, methods=['post'])
    def update_controls(self, request, pk=None):
        """به‌روزرسانی تنظیمات کنترل"""
        parent = self.get_object()
        child_id = request.data.get('child_id')
        
        try:
            child = parent.children.get(id=child_id)
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'فرزند یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # دریافت یا ایجاد تنظیمات کنترل
        control, created = ParentalControl.objects.get_or_create(
            student=child,
            defaults={'parent': parent}
        )
        
        # به‌روزرسانی تنظیمات
        serializer = ParentalControlSerializer(control, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # ثبت تغییرات در لاگ
            ParentActionLog.objects.create(
                parent=parent,
                student=child,
                action_type='control_update',
                description=f"تنظیمات کنترل به‌روزرسانی شد",
                data=request.data
            )
            
            return Response({
                'message': 'تنظیمات با موفقیت به‌روزرسانی شد',
                'controls': serializer.data
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParentActionLog(models.Model):
    """لاگ عملیات والدین"""
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    
    action_type = models.CharField(max_length=50)
    description = models.TextField()
    data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'لاگ عملیات والدین'
        verbose_name_plural = 'لاگ عملیات والدین'
```

## Monitoring Services

### Usage Monitor
```python
# educational/monitoring.py
class UsageMonitor:
    """مانیتور استفاده سیستم"""
    
    @staticmethod
    def start_session(student_profile, request):
        """شروع جلسه استفاده"""
        session = UsageSession.objects.create(
            student=student_profile,
            device_type=UsageMonitor._detect_device(request),
            ip_address=UsageMonitor._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # ذخیره session ID در cache
        cache.set(f"session:{student_profile.id}", session.id, timeout=3600)
        
        return session
    
    @staticmethod
    def end_session(student_profile):
        """پایان جلسه"""
        session_id = cache.get(f"session:{student_profile.id}")
        if session_id:
            try:
                session = UsageSession.objects.get(id=session_id)
                session.end_time = timezone.now()
                session.duration_minutes = (
                    session.end_time - session.start_time
                ).total_seconds() / 60
                session.save()
                
                # بررسی محدودیت‌های زمانی
                UsageMonitor._check_time_limits(student_profile, session)
                
            except UsageSession.DoesNotExist:
                pass
    
    @staticmethod
    def _check_time_limits(student_profile, session):
        """بررسی محدودیت‌های زمانی"""
        try:
            control = student_profile.parental_control
        except ParentalControl.DoesNotExist:
            return
        
        # محاسبه زمان استفاده امروز
        today = timezone.now().date()
        today_sessions = UsageSession.objects.filter(
            student=student_profile,
            start_time__date=today
        )
        
        total_minutes = sum(s.duration_minutes for s in today_sessions if s.duration_minutes)
        
        # بررسی محدودیت روزانه
        is_weekend = today.weekday() >= 5  # شنبه/یکشنبه
        limit = control.weekend_time_limit if is_weekend else control.daily_time_limit
        
        if total_minutes >= limit:
            # ارسال هشدار به والدین
            NotificationService.send_parent_alert(
                student_profile,
                'excessive_usage',
                f"فرزندتان امروز {total_minutes} دقیقه از سیستم استفاده کرده (حد مجاز: {limit} دقیقه)"
            )
    
    @staticmethod
    def _detect_device(request):
        """تشخیص نوع دستگاه"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        else:
            return 'desktop'
    
    @staticmethod
    def _get_client_ip(request):
        """دریافت IP کلاینت"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

### Notification Service
```python
# educational/notification_service.py
class NotificationService:
    """سرویس اعلانات"""
    
    @staticmethod
    def send_parent_alert(student_profile, alert_type, message, priority='medium', data=None):
        """ارسال هشدار به والدین"""
        parents = student_profile.parents.all()
        
        for parent in parents:
            notification = ParentNotification.objects.create(
                parent=parent,
                student=student_profile,
                notification_type=alert_type,
                priority=priority,
                title=NotificationService._get_alert_title(alert_type),
                message=message,
                data=data or {}
            )
            
            # ارسال بر اساس تنظیمات والدین
            NotificationService._send_notification(parent, notification)
    
    @staticmethod
    def _send_notification(parent, notification):
        """ارسال اعلان از طریق کانال‌های مختلف"""
        # Push Notification
        if parent.push_notifications:
            # پیاده‌سازی push notification
            notification.sent_via_push = True
        
        # SMS برای موارد فوری
        if notification.priority == 'urgent' and parent.sms_notifications:
            # ارسال SMS
            notification.sent_via_sms = True
        
        # Email برای گزارش‌های تفصیلی
        if parent.email_notifications and notification.notification_type == 'weekly_report':
            # ارسال ایمیل
            notification.sent_via_email = True
        
        notification.is_sent = True
        notification.sent_at = timezone.now()
        notification.save()
    
    @staticmethod
    def _get_alert_title(alert_type):
        """تولید عنوان هشدار"""
        titles = {
            'homework_completed': '✅ تکلیف تکمیل شد',
            'homework_overdue': '⚠️ تکلیف عقب‌افتاده',
            'achievement_earned': '🏆 دستاورد جدید',
            'low_performance': '📉 نیاز به توجه',
            'excessive_usage': '⏰ استفاده زیاد',
            'weekly_report': '📊 گزارش هفتگی',
            'system_alert': '🔔 اعلان سیستم',
        }
        return titles.get(alert_type, '🔔 اعلان')
    
    @shared_task
    def send_weekly_reports():
        """ارسال گزارش‌های هفتگی"""
        parents = ParentProfile.objects.filter(
            weekly_report=True,
            user__is_active=True
        )
        
        for parent in parents:
            for child in parent.children.all():
                report_data = WeeklyReportGenerator.generate(child)
                
                NotificationService.send_parent_alert(
                    child,
                    'weekly_report',
                    WeeklyReportGenerator.format_message(report_data),
                    priority='low',
                    data=report_data
                )

class WeeklyReportGenerator:
    """تولیدکننده گزارش هفتگی"""
    
    @staticmethod
    def generate(student_profile):
        """تولید گزارش هفتگی"""
        week_start = timezone.now().date() - timedelta(days=7)
        
        # فعالیت‌های هفته
        activities = student_profile.daily_activities.filter(
            date__gte=week_start
        )
        
        # تکالیف هفته
        homeworks = student_profile.homeworks.filter(
            assigned_date__date__gte=week_start
        )
        
        # محاسبه آمار
        total_study_time = sum(a.study_minutes for a in activities)
        completed_homeworks = homeworks.filter(status='completed').count()
        average_score = homeworks.filter(
            status='completed', score__isnull=False
        ).aggregate(avg=models.Avg('score'))['avg'] or 0
        
        # نقاط قوت و ضعف
        analyzer = PerformanceAnalyzer(student_profile)
        subject_performance = analyzer.get_subject_performance(7)
        
        best_subject = ""
        worst_subject = ""
        if subject_performance:
            best_subject = max(subject_performance.items(), key=lambda x: x[1]['average_score'])[0]
            worst_subject = min(subject_performance.items(), key=lambda x: x[1]['average_score'])[0]
        
        return {
            'student_name': student_profile.user.get_full_name(),
            'week_start': week_start,
            'week_end': timezone.now().date(),
            'total_study_minutes': total_study_time,
            'study_hours': round(total_study_time / 60, 1),
            'completed_homeworks': completed_homeworks,
            'total_homeworks': homeworks.count(),
            'completion_rate': round((completed_homeworks / homeworks.count() * 100) if homeworks.count() > 0 else 0, 1),
            'average_score': round(average_score, 1),
            'best_subject': best_subject,
            'worst_subject': worst_subject,
            'current_streak': student_profile.study_streak,
            'achievements_earned': student_profile.studentachievement_set.filter(
                earned_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        }
    
    @staticmethod
    def format_message(report_data):
        """فرمت پیام گزارش"""
        return f"""
📊 گزارش هفتگی {report_data['student_name']}

📚 مطالعه: {report_data['study_hours']} ساعت
✅ تکالیف: {report_data['completed_homeworks']}/{report_data['total_homeworks']} ({report_data['completion_rate']}%)
📈 میانگین نمره: {report_data['average_score']}
🔥 رکورد متوالی: {report_data['current_streak']} روز

💪 بهترین درس: {report_data['best_subject']}
🎯 نیاز به تمرین: {report_data['worst_subject']}

🏆 دستاوردهای جدید: {report_data['achievements_earned']}

ادامه بده عزیزم! 🌟
        """.strip()
```

## Content Safety System

### AI Content Filter
```python
# educational/safety.py
class ContentSafetyFilter:
    """فیلتر ایمنی محتوا"""
    
    # کلمات و عبارات ممنوع
    BLOCKED_KEYWORDS = [
        # اضافه شود بر اساس نیاز
    ]
    
    # موضوعات حساس
    SENSITIVE_TOPICS = [
        'سیاست', 'مذهب', 'خشونت', 'محتوای نامناسب'
    ]
    
    def __init__(self, grade_level):
        self.grade_level = grade_level
        self.filter_level = self._get_filter_level(grade_level)
    
    def _get_filter_level(self, grade_level):
        """تعیین سطح فیلتر بر اساس سن"""
        if grade_level <= 3:
            return 5  # خیلی سخت
        elif grade_level <= 6:
            return 4  # سخت
        elif grade_level <= 9:
            return 3  # متوسط
        else:
            return 2  # ملایم
    
    def filter_ai_response(self, response_text):
        """فیلتر پاسخ AI"""
        # بررسی کلمات ممنوع
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword.lower() in response_text.lower():
                return False, f"محتوا شامل کلمه نامناسب است: {keyword}"
        
        # بررسی سطح سختی زبان
        if self._is_too_complex(response_text):
            return False, "زبان پاسخ برای این سن مناسب نیست"
        
        # بررسی موضوعات حساس
        for topic in self.SENSITIVE_TOPICS:
            if self._contains_sensitive_topic(response_text, topic):
                return False, f"محتوا شامل موضوع حساس است: {topic}"
        
        return True, response_text
    
    def filter_user_input(self, user_message):
        """فیلتر ورودی کاربر"""
        # شناسایی اطلاعات شخصی
        if self._contains_personal_info(user_message):
            return False, "لطفاً اطلاعات شخصی را در پیام‌ها ذکر نکنید"
        
        # بررسی محتوای نامناسب
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword.lower() in user_message.lower():
                return False, "لطفاً از کلمات مناسب استفاده کنید"
        
        return True, user_message
    
    def _is_too_complex(self, text):
        """بررسی پیچیدگی زبان"""
        # محاسبه ساده پیچیدگی
        words = text.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # حد آستانه بر اساس پایه
        thresholds = {1: 4, 2: 4, 3: 5, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 8, 10: 9, 11: 10, 12: 10}
        threshold = thresholds.get(self.grade_level, 8)
        
        return avg_word_length > threshold
    
    def _contains_sensitive_topic(self, text, topic):
        """بررسی موضوعات حساس"""
        # پیاده‌سازی ساده - در عمل باید پیچیده‌تر باشد
        return topic.lower() in text.lower()
    
    def _contains_personal_info(self, text):
        """شناسایی اطلاعات شخصی"""
        import re
        
        # الگوهای اطلاعات شخصی
        patterns = [
            r'\b09\d{9}\b',  # شماره موبایل
            r'\b\d{10}\b',   # کد ملی
            r'\b[\w\.-]+@[\w\.-]+\.\w+\b',  # ایمیل
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        return False
```

## Middleware برای کنترل دسترسی

```python
# educational/middleware.py
class ParentalControlMiddleware:
    """Middleware کنترل والدین"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # بررسی قبل از پردازش درخواست
        if self._should_check_controls(request):
            control_result = self._check_parental_controls(request)
            if not control_result['allowed']:
                return JsonResponse(
                    {'error': control_result['reason']},
                    status=403
                )
        
        response = self.get_response(request)
        
        # بررسی بعد از پردازش (اختیاری)
        return response
    
    def _should_check_controls(self, request):
        """تعیین نیاز به بررسی کنترل"""
        # فقط برای API‌های آموزشی
        return (
            request.path.startswith('/api/educational/') and
            request.user.is_authenticated and
            hasattr(request.user, 'student_profile')
        )
    
    def _check_parental_controls(self, request):
        """بررسی کنترل‌های والدین"""
        student = request.user.student_profile
        
        try:
            control = student.parental_control
        except ParentalControl.DoesNotExist:
            return {'allowed': True}
        
        if not control.is_active:
            return {'allowed': True}
        
        # بررسی زمان مجاز
        now = timezone.now()
        current_time = now.time()
        current_day = now.weekday()
        
        if current_day not in control.allowed_weekdays:
            return {
                'allowed': False,
                'reason': 'امروز روز مجاز استفاده نیست'
            }
        
        if not (control.allowed_start_time <= current_time <= control.allowed_end_time):
            return {
                'allowed': False,
                'reason': f'ساعت مجاز استفاده: {control.allowed_start_time} تا {control.allowed_end_time}'
            }
        
        # بررسی محدودیت زمان روزانه
        today_usage = self._get_today_usage(student)
        is_weekend = current_day >= 5
        limit = control.weekend_time_limit if is_weekend else control.daily_time_limit
        
        if today_usage >= limit:
            return {
                'allowed': False,
                'reason': f'حد مجاز استفاده امروز تمام شده ({limit} دقیقه)'
            }
        
        return {'allowed': True}
    
    def _get_today_usage(self, student):
        """محاسبه زمان استفاده امروز"""
        today = timezone.now().date()
        sessions = UsageSession.objects.filter(
            student=student,
            start_time__date=today
        )
        
        return sum(s.duration_minutes for s in sessions if s.duration_minutes)
```

## Celery Tasks

### Scheduled Tasks
```python
# educational/tasks.py
from celery import shared_task
from celery.schedules import crontab
from django_celery_beat.models import PeriodicTask, CrontabSchedule

@shared_task
def check_homework_deadlines():
    """بررسی موعد تکالیف"""
    tomorrow = timezone.now() + timedelta(days=1)
    
    # تکالیف فردا
    upcoming = Homework.objects.filter(
        due_date__date=tomorrow.date(),
        status__in=['pending', 'in_progress']
    ).select_related('student', 'subject')
    
    for homework in upcoming:
        # یادآور به دانش‌آموز
        SmartReminderService.send_homework_reminder(homework)
        
        # اعلان به والدین
        NotificationService.send_parent_alert(
            homework.student,
            'homework_deadline',
            f"موعد تکلیف {homework.title} فردا است"
        )

@shared_task
def update_student_levels():
    """به‌روزرسانی سطح دانش‌آموزان"""
    students = StudentProfile.objects.all()
    
    for student in students:
        old_level = student.current_level
        
        # محاسبه سطح جدید
        level_up_points = 100  # از settings
        new_level = (student.total_points // level_up_points) + 1
        
        if new_level > old_level:
            student.current_level = new_level
            student.save()
            
            # اعلان ارتقا سطح
            NotificationService.send_parent_alert(
                student,
                'level_up',
                f"فرزندتان به سطح {new_level} ارتقا یافت!",
                priority='medium'
            )

@shared_task
def generate_daily_challenges():
    """تولید چالش‌های روزانه"""
    today = timezone.now().date()
    
    # بررسی وجود چالش امروز
    if DailyChallenge.objects.filter(date=today).exists():
        return
    
    # تولید چالش جدید
    challenge_types = [
        {
            'type': 'homework_count',
            'title': 'قهرمان تکالیف',
            'description': 'امروز 3 تکلیف تکمیل کن',
            'target': 3,
            'points': 150
        },
        {
            'type': 'study_time',
            'title': 'مطالعه‌گر پیگیر',
            'description': 'امروز 60 دقیقه مطالعه کن',
            'target': 60,
            'points': 100
        }
    ]
    
    import random
    challenge_data = random.choice(challenge_types)
    
    DailyChallenge.objects.create(
        date=today,
        title=challenge_data['title'],
        description=challenge_data['description'],
        challenge_type=challenge_data['type'],
        target_value=challenge_data['target'],
        points_reward=challenge_data['points'],
        grade_levels=list(range(1, 13))  # همه پایه‌ها
    )

# تنظیم Periodic Tasks
def setup_periodic_tasks():
    """راه‌اندازی task‌های دوره‌ای"""
    
    # هر روز ساعت 8 صبح - بررسی موعد تکالیف
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=0,
        hour=8,
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
    )
    
    PeriodicTask.objects.get_or_create(
        crontab=schedule,
        name='Check Homework Deadlines',
        task='educational.tasks.check_homework_deadlines',
    )
    
    # هر یکشنبه ساعت 20 - گزارش هفتگی
    weekly_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=0,
        hour=20,
        day_of_week=6,  # یکشنبه
        day_of_month='*',
        month_of_year='*',
    )
    
    PeriodicTask.objects.get_or_create(
        crontab=weekly_schedule,
        name='Send Weekly Reports',
        task='educational.notification_service.send_weekly_reports',
    )
```

## Testing فاز 3

```python
# educational/tests/test_parental_control.py
class ParentalControlTest(APITestCase):
    """تست‌های کنترل والدین"""
    
    def setUp(self):
        # ایجاد والدین
        self.parent_user = User.objects.create_user(
            username='parent',
            phone_number='09123456789',
            first_name='احمد',
            last_name='احمدی'
        )
        self.parent_profile = ParentProfile.objects.create(
            user=self.parent_user,
            relationship='father'
        )
        
        # ایجاد فرزند
        self.child_user = User.objects.create_user(
            username='child',
            phone_number='09123456788'
        )
        self.child_profile = StudentProfile.objects.create(
            user=self.child_user,
            grade_level=5
        )
        
        # ارتباط والدین-فرزند
        self.parent_profile.children.add(self.child_profile)
        
        # ایجاد کنترل
        self.control = ParentalControl.objects.create(
            student=self.child_profile,
            parent=self.parent_profile,
            daily_time_limit=60,  # 1 ساعت
            allowed_start_time='08:00',
            allowed_end_time='20:00'
        )
    
    def test_parent_dashboard(self):
        """تست داشبورد والدین"""
        self.client.force_authenticate(user=self.parent_user)
        
        url = reverse('parent-dashboard', kwargs={'pk': self.parent_profile.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('children', data)
        self.assertEqual(len(data['children']), 1)
        self.assertEqual(data['summary']['total_children'], 1)
    
    def test_time_limit_enforcement(self):
        """تست اعمال محدودیت زمانی"""
        # شبیه‌سازی استفاده بیش از حد
        UsageSession.objects.create(
            student=self.child_profile,
            duration_minutes=70  # بیش از حد مجاز (60 دقیقه)
        )
        
        # درخواست جدید از فرزند
        self.client.force_authenticate(user=self.child_user)
        
        url = reverse('homework-list')
        response = self.client.get(url)
        
        # باید محدود شود (در middleware)
        # این تست نیاز به پیاده‌سازی middleware دارد
```

## Deployment و Configuration

### Environment Variables
```bash
# .env اضافه کنید:
PARENTAL_CONTROL_ENABLED=true
CONTENT_FILTER_LEVEL=3
NOTIFICATION_CHANNELS=push,sms,email
WEEKLY_REPORT_TIME=20:00
EMERGENCY_ALERT_PHONE=+989123456789
```

### Celery Beat Schedule
```python
# config/settings.py اضافه کنید:
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-homework-deadlines': {
        'task': 'educational.tasks.check_homework_deadlines',
        'schedule': crontab(hour=8, minute=0),  # هر روز 8 صبح
    },
    'send-weekly-reports': {
        'task': 'educational.notification_service.send_weekly_reports',
        'schedule': crontab(hour=20, minute=0, day_of_week=6),  # یکشنبه 8 شب
    },
    'update-student-levels': {
        'task': 'educational.tasks.update_student_levels',
        'schedule': crontab(hour=0, minute=30),  # هر روز 12:30 شب
    },
    'generate-daily-challenges': {
        'task': 'educational.tasks.generate_daily_challenges',
        'schedule': crontab(hour=6, minute=0),  # هر روز 6 صبح
    },
}
```

## Success Metrics

### Parental Engagement
- [ ] Parent Registration Rate > 80%
- [ ] Weekly Report Open Rate > 60%
- [ ] Control Settings Usage > 50%
- [ ] Parent Satisfaction NPS > 70

### Child Safety
- [ ] Content Filter Accuracy > 95%
- [ ] Zero Inappropriate Content Reports
- [ ] Time Limit Compliance > 90%
- [ ] Parent Alert Response Time < 5 minutes

### System Performance
- [ ] Notification Delivery Rate > 98%
- [ ] Real-time Monitoring Accuracy > 95%
- [ ] Dashboard Load Time < 3 seconds
- [ ] Mobile App Responsiveness > 95%

---

**نکته مهم**: این فاز امنیت و کنترل والدین را تضمین می‌کند و برای کسب اعتماد خانواده‌ها ضروری است.