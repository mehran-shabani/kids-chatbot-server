# educational/views.py - Phase 1 Base Views
"""
API Views برای سیستم آموزشی فاز 1
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import timedelta

from .models import StudentProfile, Subject, Homework, HomeworkHelp, DailyActivity
from .serializers import (
    StudentProfileSerializer, SubjectSerializer, HomeworkSerializer,
    HomeworkCreateSerializer, HomeworkHelpSerializer, DailyActivitySerializer,
    StudentDashboardSerializer, WeeklyReportSerializer, SubjectProgressSerializer
)


class StudentProfileViewSet(viewsets.ModelViewSet):
    """API برای مدیریت پروفایل دانش‌آموز"""
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
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
        pending_homeworks = profile.homeworks.filter(
            status__in=['pending', 'in_progress']
        ).count()
        overdue_homeworks = profile.homeworks.filter(status='overdue').count()
        
        # تکالیف امروز
        today = timezone.now().date()
        today_homeworks = profile.homeworks.filter(
            due_date__date=today,
            status__in=['pending', 'in_progress']
        ).select_related('subject')
        
        # فعالیت‌های اخیر (7 روز گذشته)
        week_ago = today - timedelta(days=7)
        recent_activities = DailyActivity.objects.filter(
            student=profile,
            date__gte=week_ago
        ).order_by('-date')[:7]
        
        # محاسبه نرخ تکمیل
        completion_rate = 0
        if total_homeworks > 0:
            completion_rate = round((completed_homeworks / total_homeworks) * 100, 1)
        
        return Response({
            'profile': StudentProfileSerializer(profile).data,
            'stats': {
                'total_homeworks': total_homeworks,
                'completed_homeworks': completed_homeworks,
                'pending_homeworks': pending_homeworks,
                'overdue_homeworks': overdue_homeworks,
                'completion_rate': completion_rate,
                'current_streak': profile.study_streak,
                'next_level_points': profile.next_level_points
            },
            'today_homeworks': HomeworkSerializer(today_homeworks, many=True).data,
            'recent_activities': DailyActivitySerializer(recent_activities, many=True).data,
            'achievements': []  # فاز بعدی
        })
    
    @action(detail=True, methods=['get'])
    def weekly_report(self, request, pk=None):
        """گزارش هفتگی عملکرد"""
        profile = self.get_object()
        
        # محدوده هفته جاری
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # فعالیت‌های هفته
        weekly_activities = DailyActivity.objects.filter(
            student=profile,
            date__range=[week_start, week_end]
        )
        
        # آمار کلی
        total_study_minutes = sum(a.study_minutes for a in weekly_activities)
        total_homeworks_completed = sum(a.homeworks_completed for a in weekly_activities)
        total_points_earned = sum(a.points_earned for a in weekly_activities)
        
        # تکالیف هفته
        week_homeworks = profile.homeworks.filter(
            assigned_date__date__range=[week_start, week_end]
        )
        total_homeworks = week_homeworks.count()
        completion_rate = 0
        if total_homeworks > 0:
            completion_rate = round((total_homeworks_completed / total_homeworks) * 100, 1)
        
        # بهترین و ضعیف‌ترین درس
        subject_stats = {}
        for homework in week_homeworks.filter(status='completed').select_related('subject'):
            subject_name = homework.subject.persian_name
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {'count': 0, 'total_score': 0}
            subject_stats[subject_name]['count'] += 1
            if homework.score:
                subject_stats[subject_name]['total_score'] += homework.score
        
        best_subject = ""
        needs_improvement = ""
        if subject_stats:
            # محاسبه میانگین نمرات
            for subject, stats in subject_stats.items():
                if stats['count'] > 0:
                    stats['average'] = stats['total_score'] / stats['count']
            
            best_subject = max(subject_stats.items(), key=lambda x: x[1].get('average', 0))[0]
            needs_improvement = min(subject_stats.items(), key=lambda x: x[1].get('average', 100))[0]
        
        return Response({
            'week_start': week_start,
            'week_end': week_end,
            'total_study_minutes': total_study_minutes,
            'homeworks_completed': total_homeworks_completed,
            'homeworks_total': total_homeworks,
            'completion_rate': completion_rate,
            'points_earned': total_points_earned,
            'best_subject': best_subject,
            'needs_improvement': needs_improvement,
            'daily_breakdown': DailyActivitySerializer(weekly_activities, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def subject_progress(self, request, pk=None):
        """پیشرفت در هر درس"""
        profile = self.get_object()
        
        # آمار هر درس
        subjects = Subject.objects.filter(
            grade_levels__contains=[profile.grade_level]
        )
        
        progress_data = []
        for subject in subjects:
            homeworks = profile.homeworks.filter(subject=subject)
            completed = homeworks.filter(status='completed')
            
            avg_score = completed.aggregate(avg=Avg('score'))['avg'] or 0
            last_activity = homeworks.order_by('-assigned_date').first()
            
            progress_data.append({
                'subject': SubjectSerializer(subject).data,
                'total_homeworks': homeworks.count(),
                'completed_homeworks': completed.count(),
                'average_score': round(avg_score, 1),
                'completion_rate': round(
                    (completed.count() / homeworks.count() * 100) if homeworks.count() > 0 else 0, 1
                ),
                'last_activity': last_activity.assigned_date if last_activity else None
            })
        
        return Response(progress_data)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای دروس تحصیلی"""
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Subject.objects.filter(is_active=True)
        
        # فیلتر بر اساس پایه تحصیلی
        if hasattr(self.request.user, 'student_profile'):
            grade = self.request.user.student_profile.grade_level
            queryset = queryset.filter(grade_levels__contains=[grade])
        
        return queryset.order_by('order', 'persian_name')
    
    @action(detail=False, methods=['get'])
    def by_grade(self, request):
        """دروس بر اساس پایه تحصیلی"""
        grade_level = request.query_params.get('grade')
        if not grade_level:
            return Response(
                {'error': 'پایه تحصیلی مشخص نشده'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            grade_level = int(grade_level)
        except ValueError:
            return Response(
                {'error': 'پایه تحصیلی نامعتبر'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subjects = Subject.objects.filter(
            is_active=True,
            grade_levels__contains=[grade_level]
        )
        
        serializer = self.get_serializer(subjects, many=True)
        return Response(serializer.data)


class HomeworkViewSet(viewsets.ModelViewSet):
    """API برای مدیریت تکالیف"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return Homework.objects.filter(
                student=self.request.user.student_profile
            ).select_related('subject', 'student')
        return Homework.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HomeworkCreateSerializer
        return HomeworkSerializer
    
    def perform_create(self, serializer):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        serializer.save(student=student_profile)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self.request.user, 'student_profile'):
            context['student'] = self.request.user.student_profile
        return context
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """تکالیف امروز"""
        today = timezone.now().date()
        
        homeworks = self.get_queryset().filter(
            due_date__date=today,
            status__in=['pending', 'in_progress']
        )
        
        serializer = self.get_serializer(homeworks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """تکالیف آینده (7 روز آینده)"""
        today = timezone.now().date()
        week_later = today + timedelta(days=7)
        
        homeworks = self.get_queryset().filter(
            due_date__date__range=[today + timedelta(days=1), week_later],
            status__in=['pending', 'in_progress']
        )
        
        serializer = self.get_serializer(homeworks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """تکالیف عقب‌افتاده"""
        now = timezone.now()
        
        homeworks = self.get_queryset().filter(
            due_date__lt=now,
            status__in=['pending', 'in_progress']
        )
        
        # به‌روزرسانی وضعیت به overdue
        homeworks.update(status='overdue')
        
        serializer = self.get_serializer(homeworks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """علامت‌گذاری تکلیف به عنوان تکمیل شده"""
        homework = self.get_object()
        
        # دریافت نمره از request (اختیاری)
        score = request.data.get('score')
        feedback = request.data.get('feedback', '')
        
        # تکمیل تکلیف
        result = homework.mark_completed(score=score, feedback=feedback)
        
        return Response({
            'message': '🎉 آفرین! تکلیف با موفقیت تکمیل شد!',
            'homework': HomeworkSerializer(homework).data,
            'points_result': result
        })
    
    @action(detail=True, methods=['post'])
    def start_working(self, request, pk=None):
        """شروع کار روی تکلیف"""
        homework = self.get_object()
        
        if homework.status == 'pending':
            homework.status = 'in_progress'
            homework.save()
            
            # افزایش view count
            homework.view_count += 1
            homework.save(update_fields=['view_count'])
            
            return Response({
                'message': 'شروع کار روی تکلیف ثبت شد!',
                'homework': HomeworkSerializer(homework).data
            })
        else:
            return Response(
                {'error': 'تکلیف قبلاً شروع شده یا تکمیل شده'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def request_help(self, request, pk=None):
        """درخواست کمک برای تکلیف"""
        homework = self.get_object()
        question = request.data.get('question', '').strip()
        
        if not question:
            return Response(
                {'error': 'لطفاً سوال خود را بنویسید'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ایجاد درخواست کمک
        help_request = HomeworkHelp.objects.create(
            homework=homework,
            question=question
        )
        
        # علامت‌گذاری درخواست کمک در تکلیف
        homework.help_requested = True
        homework.save(update_fields=['help_requested'])
        
        # TODO: فراخوانی AI برای پاسخ (فاز بعدی)
        ai_response = "سوال شما ثبت شد. به زودی پاسخ دریافت خواهید کرد."
        help_request.ai_response = ai_response
        help_request.save()
        
        return Response({
            'message': 'درخواست کمک ثبت شد!',
            'help_request': HomeworkHelpSerializer(help_request).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """آمار کلی تکالیف"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'completed': queryset.filter(status='completed').count(),
            'pending': queryset.filter(status='pending').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'overdue': queryset.filter(status='overdue').count(),
        }
        
        # آمار امتیازات
        student_profile = request.user.student_profile
        stats.update({
            'total_points': student_profile.total_points,
            'current_level': student_profile.current_level,
            'study_streak': student_profile.study_streak,
        })
        
        return Response(stats)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای دروس تحصیلی"""
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Subject.objects.filter(is_active=True)
        
        # فیلتر بر اساس پایه تحصیلی کاربر
        if hasattr(self.request.user, 'student_profile'):
            grade = self.request.user.student_profile.grade_level
            queryset = queryset.filter(grade_levels__contains=[grade])
        
        return queryset.order_by('order', 'persian_name')
    
    @action(detail=False, methods=['get'])
    def by_grade(self, request):
        """دروس بر اساس پایه تحصیلی مشخص"""
        grade_level = request.query_params.get('grade')
        if not grade_level:
            return Response(
                {'error': 'پارامتر grade الزامی است'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            grade_level = int(grade_level)
            if not 1 <= grade_level <= 12:
                raise ValueError()
        except ValueError:
            return Response(
                {'error': 'پایه تحصیلی باید عددی بین 1 تا 12 باشد'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subjects = Subject.objects.filter(
            is_active=True,
            grade_levels__contains=[grade_level]
        ).order_by('order', 'persian_name')
        
        serializer = self.get_serializer(subjects, many=True)
        return Response(serializer.data)


class HomeworkViewSet(viewsets.ModelViewSet):
    """API برای مدیریت تکالیف"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return Homework.objects.filter(
                student=self.request.user.student_profile
            ).select_related('subject').prefetch_related('help_requests')
        return Homework.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HomeworkCreateSerializer
        return HomeworkSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if hasattr(self.request.user, 'student_profile'):
            context['student'] = self.request.user.student_profile
        return context
    
    def perform_create(self, serializer):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        serializer.save(student=student_profile)
    
    def list(self, request):
        """لیست تکالیف با فیلتر"""
        queryset = self.get_queryset()
        
        # فیلترها
        status_filter = request.query_params.get('status')
        subject_filter = request.query_params.get('subject')
        date_filter = request.query_params.get('date')  # today, week, month
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if subject_filter:
            queryset = queryset.filter(subject__name=subject_filter)
        
        if date_filter == 'today':
            today = timezone.now().date()
            queryset = queryset.filter(due_date__date=today)
        elif date_filter == 'week':
            today = timezone.now().date()
            week_end = today + timedelta(days=7)
            queryset = queryset.filter(due_date__date__range=[today, week_end])
        elif date_filter == 'month':
            today = timezone.now().date()
            month_end = today + timedelta(days=30)
            queryset = queryset.filter(due_date__date__range=[today, month_end])
        
        # مرتب‌سازی
        ordering = request.query_params.get('ordering', '-due_date')
        queryset = queryset.order_by(ordering)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """تکالیف امروز"""
        today = timezone.now().date()
        homeworks = self.get_queryset().filter(
            due_date__date=today,
            status__in=['pending', 'in_progress']
        )
        
        serializer = self.get_serializer(homeworks, many=True)
        return Response({
            'count': homeworks.count(),
            'homeworks': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """تکالیف عقب‌افتاده"""
        now = timezone.now()
        homeworks = self.get_queryset().filter(
            due_date__lt=now,
            status__in=['pending', 'in_progress']
        )
        
        # به‌روزرسانی وضعیت
        homeworks.update(status='overdue')
        
        serializer = self.get_serializer(homeworks, many=True)
        return Response({
            'count': homeworks.count(),
            'homeworks': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """تکمیل تکلیف"""
        homework = self.get_object()
        
        if homework.status == 'completed':
            return Response(
                {'error': 'این تکلیف قبلاً تکمیل شده'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        score = request.data.get('score')
        feedback = request.data.get('feedback', '')
        
        # اعتبارسنجی نمره
        if score is not None:
            try:
                score = int(score)
                if not 0 <= score <= 100:
                    return Response(
                        {'error': 'نمره باید بین 0 تا 100 باشد'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'نمره باید عدد باشد'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # تکمیل تکلیف
        result = homework.mark_completed(score=score, feedback=feedback)
        
        # به‌روزرسانی فعالیت روزانه
        activity = DailyActivity.get_or_create_today(homework.student)
        activity.homeworks_completed += 1
        activity.points_earned += result['points_added']
        
        # اضافه کردن درس به لیست مطالعه شده
        if homework.subject.id not in activity.subjects_studied:
            activity.subjects_studied.append(homework.subject.id)
        
        activity.save()
        
        return Response({
            'message': '🎉 آفرین! تکلیف با موفقیت تکمیل شد!',
            'homework': HomeworkSerializer(homework).data,
            'points_result': result,
            'new_streak': homework.student.study_streak
        })
    
    @action(detail=True, methods=['post'])
    def start_working(self, request, pk=None):
        """شروع کار روی تکلیف"""
        homework = self.get_object()
        
        if homework.status != 'pending':
            return Response(
                {'error': 'فقط می‌توان تکالیف در انتظار را شروع کرد'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        homework.status = 'in_progress'
        homework.view_count += 1
        homework.save()
        
        return Response({
            'message': 'شروع کار روی تکلیف ثبت شد!',
            'homework': HomeworkSerializer(homework).data
        })
    
    @action(detail=True, methods=['post'])
    def request_help(self, request, pk=None):
        """درخواست کمک برای تکلیف"""
        homework = self.get_object()
        question = request.data.get('question', '').strip()
        
        if not question:
            return Response(
                {'error': 'لطفاً سوال خود را بنویسید'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(question) < 10:
            return Response(
                {'error': 'سوال خیلی کوتاه است. لطفاً بیشتر توضیح دهید'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ایجاد درخواست کمک
        help_request = HomeworkHelp.objects.create(
            homework=homework,
            question=question
        )
        
        # علامت‌گذاری درخواست کمک
        homework.help_requested = True
        homework.save(update_fields=['help_requested'])
        
        # پاسخ پایه (در فاز بعدی با AI جایگزین می‌شود)
        basic_response = f"""
        سوال شما درباره {homework.subject.persian_name} ثبت شد.
        
        برای حل این مسئله، این مراحل را دنبال کنید:
        1. ابتدا سوال را به دقت بخوانید
        2. اطلاعات مهم را مشخص کنید
        3. روش حل را انتخاب کنید
        4. گام به گام حل کنید
        
        اگر باز هم مشکل دارید، سوال دقیق‌تری بپرسید.
        """
        
        help_request.ai_response = basic_response
        help_request.save()
        
        # به‌روزرسانی آمار سوالات
        activity = DailyActivity.get_or_create_today(homework.student)
        activity.questions_asked += 1
        activity.save()
        
        return Response({
            'message': 'درخواست کمک ثبت شد!',
            'help_request': HomeworkHelpSerializer(help_request).data
        })
    
    @action(detail=False, methods=['get'])
    def by_subject(self, request):
        """تکالیف بر اساس درس"""
        subject_id = request.query_params.get('subject_id')
        if not subject_id:
            return Response(
                {'error': 'پارامتر subject_id الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        homeworks = self.get_queryset().filter(subject_id=subject_id)
        serializer = self.get_serializer(homeworks, many=True)
        
        return Response({
            'subject_id': subject_id,
            'count': homeworks.count(),
            'homeworks': serializer.data
        })


class DailyActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """API برای مشاهده فعالیت‌های روزانه"""
    serializer_class = DailyActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return DailyActivity.objects.filter(
                student=self.request.user.student_profile
            ).order_by('-date')
        return DailyActivity.objects.none()
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """فعالیت امروز"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'پروفایل دانش‌آموز یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        activity = DailyActivity.get_or_create_today(request.user.student_profile)
        serializer = self.get_serializer(activity)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def weekly(self, request):
        """فعالیت هفته جاری"""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        activities = self.get_queryset().filter(
            date__gte=week_start,
            date__lte=today
        )
        
        serializer = self.get_serializer(activities, many=True)
        
        # آمار خلاصه
        total_minutes = sum(a.study_minutes for a in activities)
        total_homeworks = sum(a.homeworks_completed for a in activities)
        total_points = sum(a.points_earned for a in activities)
        
        return Response({
            'week_start': week_start,
            'week_end': today,
            'daily_activities': serializer.data,
            'summary': {
                'total_study_minutes': total_minutes,
                'total_homeworks_completed': total_homeworks,
                'total_points_earned': total_points,
                'average_daily_minutes': round(total_minutes / 7, 1),
            }
        })


# Helper Views برای عملیات خاص
class QuickActionsViewSet(viewsets.ViewSet):
    """API برای عملیات سریع"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def add_study_time(self, request):
        """ثبت زمان مطالعه"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'پروفایل دانش‌آموز یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        minutes = request.data.get('minutes')
        subject_id = request.data.get('subject_id')
        
        try:
            minutes = int(minutes)
            if minutes <= 0 or minutes > 480:  # حداکثر 8 ساعت
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'زمان مطالعه باید عددی بین 1 تا 480 دقیقه باشد'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # به‌روزرسانی فعالیت روزانه
        activity = DailyActivity.get_or_create_today(request.user.student_profile)
        activity.study_minutes += minutes
        
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
                if subject.id not in activity.subjects_studied:
                    activity.subjects_studied.append(subject.id)
            except Subject.DoesNotExist:
                pass
        
        activity.save()
        
        # اضافه کردن امتیاز برای مطالعه
        points = max(1, minutes // 10)  # هر 10 دقیقه 1 امتیاز
        result = request.user.student_profile.add_points(points, "مطالعه")
        
        return Response({
            'message': f'🎉 {minutes} دقیقه مطالعه ثبت شد!',
            'activity': DailyActivitySerializer(activity).data,
            'points_result': result
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """خلاصه داشبورد سریع"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'پروفایل دانش‌آموز یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        profile = request.user.student_profile
        today = timezone.now().date()
        
        # تکالیف امروز
        today_homeworks = profile.homeworks.filter(
            due_date__date=today,
            status__in=['pending', 'in_progress']
        ).count()
        
        # تکالیف عقب‌افتاده
        overdue_homeworks = profile.homeworks.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        # فعالیت امروز
        today_activity = DailyActivity.get_or_create_today(profile)
        
        return Response({
            'student_name': profile.user.get_full_name() or profile.user.username,
            'grade_level': profile.grade_level,
            'current_level': profile.current_level,
            'total_points': profile.total_points,
            'study_streak': profile.study_streak,
            'today_homeworks': today_homeworks,
            'overdue_homeworks': overdue_homeworks,
            'today_study_minutes': today_activity.study_minutes,
            'daily_goal': profile.daily_study_goal,
            'goal_progress': round(
                (today_activity.study_minutes / profile.daily_study_goal) * 100, 1
            ) if profile.daily_study_goal > 0 else 0
        })


# کلاس‌های کمکی برای validation و utilities
class HomeworkValidationMixin:
    """Mixin برای اعتبارسنجی تکالیف"""
    
    def validate_homework_access(self, homework, user):
        """بررسی دسترسی کاربر به تکلیف"""
        if not hasattr(user, 'student_profile'):
            return False, "پروفایل دانش‌آموز یافت نشد"
        
        if homework.student != user.student_profile:
            return False, "شما به این تکلیف دسترسی ندارید"
        
        return True, ""
    
    def validate_homework_status_change(self, homework, new_status):
        """بررسی امکان تغییر وضعیت تکلیف"""
        valid_transitions = {
            'pending': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'pending'],
            'completed': ['reviewed'],
            'overdue': ['completed', 'cancelled'],
            'reviewed': [],
            'cancelled': ['pending']
        }
        
        if new_status not in valid_transitions.get(homework.status, []):
            return False, f"نمی‌توان از وضعیت {homework.get_status_display()} به {new_status} تغییر کرد"
        
        return True, ""