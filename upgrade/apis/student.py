# Student API Documentation
"""
مستندات کامل API‌های دانش‌آموز
"""

## Student Profile APIs

### GET /api/educational/profiles/
دریافت لیست پروفایل‌های دانش‌آموز کاربر جاری

**Response:**
```json
[
    {
        "id": 1,
        "grade_level": 5,
        "school_type": "public",
        "total_points": 250,
        "current_level": 3,
        "study_streak": 5
    }
]
```

### POST /api/educational/profiles/
ایجاد پروفایل جدید

**Request:**
```json
{
    "grade_level": 5,
    "school_type": "public",
    "learning_style": "visual",
    "daily_study_goal": 60
}
```

### GET /api/educational/profiles/{id}/dashboard/
داشبورد کامل دانش‌آموز

**Response:**
```json
{
    "profile": {...},
    "stats": {
        "total_homeworks": 25,
        "completed_homeworks": 20,
        "completion_rate": 80.0
    },
    "today_homeworks": [...],
    "achievements": [...]
}
```

## Homework APIs

### GET /api/educational/homeworks/
لیست تکالیف با فیلتر

**Query Parameters:**
- status: pending|in_progress|completed|overdue
- subject: نام درس
- date: today|week|month

### POST /api/educational/homeworks/
ایجاد تکلیف جدید

### POST /api/educational/homeworks/{id}/mark_complete/
تکمیل تکلیف

**Request:**
```json
{
    "score": 85,
    "feedback": "عالی بود!"
}
```

**Response:**
```json
{
    "message": "🎉 آفرین! تکلیف تکمیل شد!",
    "points_result": {
        "points_added": 36,
        "level_up": true,
        "new_level": 4
    }
}
```