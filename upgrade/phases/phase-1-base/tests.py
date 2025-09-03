# educational/tests.py - Phase 1 Base Tests
"""
تست‌های جامع برای فاز 1 سیستم آموزشی
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta, date

from .models import StudentProfile, Subject, Homework, HomeworkHelp, DailyActivity

User = get_user_model()


class StudentProfileModelTest(TestCase):
    """تست‌های مدل StudentProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789',
            first_name='علی',
            last_name='احمدی'
        )
    
    def test_create_student_profile(self):
        """تست ایجاد پروفایل دانش‌آموز"""
        profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5,
            school_type='public',
            daily_study_goal=90,
            learning_style='visual'
        )
        
        self.assertEqual(profile.grade_level, 5)
        self.assertEqual(profile.total_points, 0)
        self.assertEqual(profile.current_level, 1)
        self.assertEqual(profile.study_streak, 0)
        self.assertEqual(str(profile), "علی احمدی - پایه 5")
    
    def test_age_calculation(self):
        """تست محاسبه سن"""
        birth_date = date(2010, 5, 15)
        profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5,
            birth_date=birth_date
        )
        
        expected_age = date.today().year - 2010
        if (date.today().month, date.today().day) < (5, 15):
            expected_age -= 1
        
        self.assertEqual(profile.age, expected_age)
    
    def test_add_points_and_level_up(self):
        """تست اضافه کردن امتیاز و ارتقا سطح"""
        profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5
        )
        
        # اضافه کردن 50 امتیاز
        result = profile.add_points(50, "تست")
        
        self.assertEqual(result['points_added'], 50)
        self.assertEqual(result['total_points'], 50)
        self.assertEqual(result['level_up'], False)
        self.assertEqual(profile.total_points, 50)
        
        # اضافه کردن 60 امتیاز دیگر (مجموع 110 -> سطح 2)
        result = profile.add_points(60, "تست 2")
        
        self.assertEqual(result['level_up'], True)
        self.assertEqual(result['new_level'], 2)
        self.assertEqual(profile.current_level, 2)
    
    def test_study_streak_update(self):
        """تست به‌روزرسانی رکورد مطالعه"""
        profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5
        )
        
        # اولین بار
        streak = profile.update_study_streak()
        self.assertEqual(streak, 1)
        
        # همان روز (نباید تغییر کند)
        streak = profile.update_study_streak()
        self.assertEqual(streak, 1)
        
        # شبیه‌سازی روز قبل
        profile.last_activity_date = timezone.now().date() - timedelta(days=1)
        profile.save()
        
        streak = profile.update_study_streak()
        self.assertEqual(streak, 2)


class SubjectModelTest(TestCase):
    """تست‌های مدل Subject"""
    
    def test_create_subject(self):
        """تست ایجاد درس"""
        subject = Subject.objects.create(
            name='math',
            persian_name='ریاضی',
            color_code='#e74c3c',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
        
        self.assertEqual(str(subject), 'ریاضی')
        self.assertTrue(subject.is_available_for_grade(3))
        self.assertFalse(subject.is_available_for_grade(7))


class HomeworkModelTest(TestCase):
    """تست‌های مدل Homework"""
    
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
            persian_name='ریاضی',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
    
    def test_create_homework(self):
        """تست ایجاد تکلیف"""
        due_date = timezone.now() + timedelta(days=2)
        homework = Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تمرین ضرب',
            description='حل مسائل صفحه 25',
            due_date=due_date,
            difficulty=2
        )
        
        self.assertEqual(homework.status, 'pending')
        self.assertEqual(homework.points_value, 20)
        self.assertFalse(homework.is_overdue)
        self.assertEqual(homework.get_grade_level(), 5)
    
    def test_homework_completion(self):
        """تست تکمیل تکلیف"""
        homework = Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تست',
            description='تست',
            due_date=timezone.now() + timedelta(days=1),
            difficulty=3
        )
        
        initial_points = self.profile.total_points
        result = homework.mark_completed(score=85, feedback="عالی بود!")
        
        self.assertEqual(homework.status, 'completed')
        self.assertEqual(homework.score, 85)
        self.assertIsNotNone(homework.completion_date)
        
        # بررسی امتیاز (30 امتیاز + 20% بونوس = 36)
        self.profile.refresh_from_db()
        expected_points = initial_points + 36  # 30 * 1.2
        self.assertEqual(self.profile.total_points, expected_points)
    
    def test_overdue_homework(self):
        """تست تکلیف عقب‌افتاده"""
        past_date = timezone.now() - timedelta(days=1)
        homework = Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تست عقب‌افتاده',
            description='تست',
            due_date=past_date
        )
        
        self.assertTrue(homework.is_overdue)
        self.assertEqual(homework.time_remaining, "گذشته از موعد")


# API Tests
class StudentProfileAPITest(APITestCase):
    """تست‌های API پروفایل دانش‌آموز"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_student_profile(self):
        """تست ایجاد پروفایل از طریق API"""
        url = reverse('student-profile-list')
        data = {
            'grade_level': 5,
            'school_type': 'public',
            'learning_style': 'visual',
            'daily_study_goal': 60
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentProfile.objects.count(), 1)
        
        profile = StudentProfile.objects.first()
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.grade_level, 5)
    
    def test_dashboard_api(self):
        """تست API داشبورد"""
        profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5
        )
        
        url = reverse('student-profile-dashboard', kwargs={'pk': profile.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('profile', data)
        self.assertIn('stats', data)
        self.assertIn('today_homeworks', data)
        self.assertEqual(data['stats']['total_homeworks'], 0)


class SubjectAPITest(APITestCase):
    """تست‌های API دروس"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5
        )
        self.client.force_authenticate(user=self.user)
        
        # ایجاد دروس تست
        self.math = Subject.objects.create(
            name='math',
            persian_name='ریاضی',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
        self.science = Subject.objects.create(
            name='science',
            persian_name='علوم',
            grade_levels=[3, 4, 5, 6, 7, 8]
        )
        self.high_school_math = Subject.objects.create(
            name='advanced_math',
            persian_name='ریاضی پیشرفته',
            grade_levels=[10, 11, 12]
        )
    
    def test_get_subjects_for_grade(self):
        """تست دریافت دروس مناسب پایه"""
        url = reverse('subject-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subjects = response.json()
        
        # باید فقط دروس مناسب پایه 5 برگردد
        subject_names = [s['name'] for s in subjects]
        self.assertIn('math', subject_names)
        self.assertIn('science', subject_names)
        self.assertNotIn('advanced_math', subject_names)
    
    def test_subjects_by_grade_api(self):
        """تست API دروس بر اساس پایه مشخص"""
        url = reverse('subject-by-grade')
        response = self.client.get(url, {'grade': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subjects = response.json()
        
        subject_names = [s['name'] for s in subjects]
        self.assertIn('advanced_math', subject_names)


class HomeworkAPITest(APITestCase):
    """تست‌های API تکالیف"""
    
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
            persian_name='ریاضی',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_homework(self):
        """تست ایجاد تکلیف"""
        url = reverse('homework-list')
        due_date = timezone.now() + timedelta(days=2)
        
        data = {
            'title': 'تمرین ضرب',
            'description': 'حل مسائل صفحه 25',
            'subject': self.subject.id,
            'due_date': due_date.isoformat(),
            'estimated_minutes': 45,
            'difficulty': 2
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Homework.objects.count(), 1)
        
        homework = Homework.objects.first()
        self.assertEqual(homework.student, self.profile)
        self.assertEqual(homework.title, 'تمرین ضرب')
    
    def test_mark_homework_complete(self):
        """تست تکمیل تکلیف"""
        homework = Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تست',
            description='تست',
            due_date=timezone.now() + timedelta(days=1),
            difficulty=3
        )
        
        url = reverse('homework-mark-complete', kwargs={'pk': homework.id})
        response = self.client.post(url, {'score': 90, 'feedback': 'عالی!'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        homework.refresh_from_db()
        self.assertEqual(homework.status, 'completed')
        self.assertEqual(homework.score, 90)
        
        # بررسی امتیاز (30 امتیاز + 20% بونوس = 36)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_points, 36)
    
    def test_homework_filters(self):
        """تست فیلترهای تکالیف"""
        # ایجاد تکالیف مختلف
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # تکلیف امروز
        Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تکلیف امروز',
            description='تست',
            due_date=timezone.datetime.combine(today, timezone.datetime.min.time()).replace(tzinfo=timezone.get_current_timezone()),
            difficulty=2
        )
        
        # تکلیف فردا
        Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تکلیف فردا',
            description='تست',
            due_date=timezone.datetime.combine(tomorrow, timezone.datetime.min.time()).replace(tzinfo=timezone.get_current_timezone()),
            difficulty=3
        )
        
        # تست فیلتر امروز
        url = reverse('homework-today')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['homeworks'][0]['title'], 'تکلیف امروز')
    
    def test_request_help(self):
        """تست درخواست کمک"""
        homework = Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تست',
            description='تست',
            due_date=timezone.now() + timedelta(days=1),
            difficulty=2
        )
        
        url = reverse('homework-request-help', kwargs={'pk': homework.id})
        response = self.client.post(url, {
            'question': 'چطور این مسئله را حل کنم؟'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(HomeworkHelp.objects.count(), 1)
        
        help_request = HomeworkHelp.objects.first()
        self.assertEqual(help_request.homework, homework)
        self.assertIn('چطور', help_request.question)


class DailyActivityTest(TestCase):
    """تست‌های فعالیت روزانه"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5
        )
    
    def test_get_or_create_today_activity(self):
        """تست دریافت یا ایجاد فعالیت امروز"""
        # اولین بار - باید ایجاد شود
        activity = DailyActivity.get_or_create_today(self.profile)
        self.assertEqual(activity.student, self.profile)
        self.assertEqual(activity.date, timezone.now().date())
        self.assertEqual(activity.study_minutes, 0)
        
        # دومین بار - باید همان رکورد برگردد
        activity2 = DailyActivity.get_or_create_today(self.profile)
        self.assertEqual(activity.id, activity2.id)


class IntegrationTest(APITestCase):
    """تست‌های ادغام سیستم"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789',
            first_name='سارا',
            last_name='کریمی'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5,
            daily_study_goal=60
        )
        self.subject = Subject.objects.create(
            name='math',
            persian_name='ریاضی',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
        self.client.force_authenticate(user=self.user)
    
    def test_complete_homework_workflow(self):
        """تست فرآیند کامل انجام تکلیف"""
        
        # 1. ایجاد تکلیف
        url = reverse('homework-list')
        due_date = timezone.now() + timedelta(days=2)
        
        data = {
            'title': 'تمرین جمع',
            'description': 'حل 10 مسئله جمع',
            'subject': self.subject.id,
            'due_date': due_date.isoformat(),
            'estimated_minutes': 30,
            'difficulty': 2
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        homework_id = response.json()['id']
        
        # 2. شروع کار روی تکلیف
        url = reverse('homework-start-working', kwargs={'pk': homework_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        homework = Homework.objects.get(id=homework_id)
        self.assertEqual(homework.status, 'in_progress')
        
        # 3. درخواست کمک
        url = reverse('homework-request-help', kwargs={'pk': homework_id})
        response = self.client.post(url, {
            'question': 'عدد 25 + 17 چقدر می‌شود؟'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. تکمیل تکلیف
        url = reverse('homework-mark-complete', kwargs={'pk': homework_id})
        response = self.client.post(url, {
            'score': 95,
            'feedback': 'همه جواب‌ها درست بود!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی نتایج
        homework.refresh_from_db()
        self.assertEqual(homework.status, 'completed')
        self.assertEqual(homework.score, 95)
        
        # بررسی فعالیت روزانه
        activity = DailyActivity.objects.filter(
            student=self.profile,
            date=timezone.now().date()
        ).first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.homeworks_completed, 1)
        self.assertGreater(activity.points_earned, 0)
    
    def test_dashboard_data_integrity(self):
        """تست یکپارچگی داده‌های داشبورد"""
        
        # ایجاد چند تکلیف
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # تکلیف امروز
        Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تکلیف امروز',
            description='تست',
            due_date=timezone.datetime.combine(today, timezone.datetime.min.time()).replace(tzinfo=timezone.get_current_timezone())
        )
        
        # تکلیف تکمیل شده
        completed_homework = Homework.objects.create(
            student=self.profile,
            subject=self.subject,
            title='تکلیف تکمیل شده',
            description='تست',
            due_date=timezone.now() + timedelta(days=1),
            status='completed',
            completion_date=timezone.now()
        )
        
        # دریافت داشبورد
        url = reverse('student-profile-dashboard', kwargs={'pk': self.profile.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # بررسی آمار
        self.assertEqual(data['stats']['total_homeworks'], 2)
        self.assertEqual(data['stats']['completed_homeworks'], 1)
        self.assertEqual(data['stats']['pending_homeworks'], 1)
        self.assertEqual(data['stats']['completion_rate'], 50.0)


class QuickActionsAPITest(APITestCase):
    """تست‌های API عملیات سریع"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5,
            daily_study_goal=60
        )
        self.subject = Subject.objects.create(
            name='math',
            persian_name='ریاضی',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
        self.client.force_authenticate(user=self.user)
    
    def test_add_study_time(self):
        """تست ثبت زمان مطالعه"""
        url = reverse('quickactions-add-study-time')
        response = self.client.post(url, {
            'minutes': 30,
            'subject_id': self.subject.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی فعالیت روزانه
        activity = DailyActivity.objects.filter(
            student=self.profile,
            date=timezone.now().date()
        ).first()
        
        self.assertIsNotNone(activity)
        self.assertEqual(activity.study_minutes, 30)
        self.assertIn(self.subject.id, activity.subjects_studied)
        
        # بررسی امتیاز
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_points, 3)  # 30 // 10 = 3
    
    def test_dashboard_summary(self):
        """تست خلاصه داشبورد"""
        url = reverse('quickactions-dashboard-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['grade_level'], 5)
        self.assertEqual(data['current_level'], 1)
        self.assertEqual(data['total_points'], 0)
        self.assertEqual(data['today_homeworks'], 0)
        self.assertEqual(data['daily_goal'], 60)


class ValidationTest(TestCase):
    """تست‌های اعتبارسنجی"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
    
    def test_invalid_grade_level(self):
        """تست پایه تحصیلی نامعتبر"""
        with self.assertRaises(Exception):
            StudentProfile.objects.create(
                user=self.user,
                grade_level=15  # نامعتبر
            )
    
    def test_invalid_study_goal(self):
        """تست هدف مطالعه نامعتبر"""
        from .serializers import StudentProfileSerializer
        
        data = {
            'grade_level': 5,
            'daily_study_goal': 500  # بیش از حد
        }
        
        serializer = StudentProfileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('daily_study_goal', serializer.errors)
    
    def test_past_due_date(self):
        """تست موعد گذشته"""
        from .serializers import HomeworkCreateSerializer
        
        past_date = timezone.now() - timedelta(days=1)
        data = {
            'title': 'تست',
            'description': 'تست',
            'subject': 1,
            'due_date': past_date.isoformat(),
            'difficulty': 2
        }
        
        serializer = HomeworkCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('due_date', serializer.errors)


# Performance Tests
class PerformanceTest(APITestCase):
    """تست‌های عملکرد"""
    
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
            persian_name='ریاضی',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_with_many_homeworks(self):
        """تست داشبورد با تعداد زیاد تکلیف"""
        # ایجاد 100 تکلیف
        homeworks = []
        for i in range(100):
            homework = Homework(
                student=self.profile,
                subject=self.subject,
                title=f'تکلیف {i}',
                description='تست',
                due_date=timezone.now() + timedelta(days=i % 7),
                difficulty=(i % 5) + 1
            )
            homeworks.append(homework)
        
        Homework.objects.bulk_create(homeworks)
        
        # تست سرعت داشبورد
        import time
        start_time = time.time()
        
        url = reverse('student-profile-dashboard', kwargs={'pk': self.profile.id})
        response = self.client.get(url)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 2.0)  # کمتر از 2 ثانیه
        
        # بررسی صحت آمار
        data = response.json()
        self.assertEqual(data['stats']['total_homeworks'], 100)


# Edge Cases Tests
class EdgeCaseTest(TestCase):
    """تست‌های موارد خاص"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            phone_number='09123456789'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            grade_level=5
        )
    
    def test_homework_without_subject(self):
        """تست تکلیف بدون درس"""
        with self.assertRaises(Exception):
            Homework.objects.create(
                student=self.profile,
                title='تست',
                description='تست',
                due_date=timezone.now() + timedelta(days=1)
                # subject نداده نشده
            )
    
    def test_negative_points(self):
        """تست امتیاز منفی"""
        result = self.profile.add_points(-10, "جریمه")
        
        # امتیاز نمی‌تواند منفی شود
        self.assertEqual(self.profile.total_points, 0)
    
    def test_extreme_study_time(self):
        """تست زمان مطالعه غیرعادی"""
        activity = DailyActivity.get_or_create_today(self.profile)
        
        # 10 ساعت مطالعه (غیرعادی اما مجاز)
        activity.study_minutes = 600
        activity.save()
        
        self.assertEqual(activity.study_minutes, 600)


# Security Tests  
class SecurityTest(APITestCase):
    """تست‌های امنیتی"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='student1',
            phone_number='09123456789'
        )
        self.user2 = User.objects.create_user(
            username='student2', 
            phone_number='09123456788'
        )
        
        self.profile1 = StudentProfile.objects.create(
            user=self.user1,
            grade_level=5
        )
        self.profile2 = StudentProfile.objects.create(
            user=self.user2,
            grade_level=6
        )
        
        self.subject = Subject.objects.create(
            name='math',
            persian_name='ریاضی',
            grade_levels=[1, 2, 3, 4, 5, 6]
        )
    
    def test_homework_access_control(self):
        """تست کنترل دسترسی تکالیف"""
        # ایجاد تکلیف برای کاربر 1
        homework = Homework.objects.create(
            student=self.profile1,
            subject=self.subject,
            title='تکلیف خصوصی',
            description='تست',
            due_date=timezone.now() + timedelta(days=1)
        )
        
        # کاربر 2 نباید به تکلیف کاربر 1 دسترسی داشته باشد
        self.client.force_authenticate(user=self.user2)
        
        url = reverse('homework-detail', kwargs={'pk': homework.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unauthorized_access(self):
        """تست دسترسی غیرمجاز"""
        # بدون احراز هویت
        self.client.force_authenticate(user=None)
        
        url = reverse('homework-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)