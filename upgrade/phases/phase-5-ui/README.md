# Phase 5: Child-Friendly UI/UX
## فاز 5: رابط کاربری کودک‌محور (Agent UI)

**مدت**: 2 هفته | **Agent**: UI Agent | **وابستگی**: Phases 1-4

## اهداف

### هدف اصلی
طراحی و پیاده‌سازی رابط کاربری جذاب و کودک‌محور

### ویژگی‌های UI/UX
1. **طراحی واکنش‌گرا**: موبایل، تبلت، دسکتاپ
2. **انیمیشن‌های جذاب**: تعاملات زنده
3. **تم‌های متنوع**: شخصی‌سازی ظاهر
4. **دسترسی‌پذیری**: مناسب همه کودکان
5. **عناصر بازی‌گونه**: UI gamified

## Frontend Structure

### React Components
```jsx
// components/StudentDashboard.jsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const StudentDashboard = ({ studentId }) => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchDashboardData();
    }, [studentId]);
    
    const fetchDashboardData = async () => {
        try {
            const response = await fetch(`/api/educational/profiles/${studentId}/dashboard/`);
            const data = await response.json();
            setDashboardData(data);
        } catch (error) {
            console.error('خطا در دریافت داده‌ها:', error);
        } finally {
            setLoading(false);
        }
    };
    
    if (loading) return <LoadingSpinner />;
    
    return (
        <div className="student-dashboard">
            <WelcomeHeader student={dashboardData.profile} />
            <ProgressOverview stats={dashboardData.stats} />
            <TodayHomeworks homeworks={dashboardData.today_homeworks} />
            <QuickActions />
        </div>
    );
};

// components/HomeworkCard.jsx
const HomeworkCard = ({ homework, onComplete }) => {
    return (
        <motion.div 
            className={`homework-card difficulty-${homework.difficulty}`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
        >
            <div className="homework-header">
                <SubjectIcon 
                    subject={homework.subject_name}
                    color={homework.subject_color}
                />
                <div className="homework-info">
                    <h3>{homework.title}</h3>
                    <p className="subject">{homework.subject_name}</p>
                </div>
                <DifficultyStars count={homework.difficulty} />
            </div>
            
            <div className="homework-body">
                <p>{homework.description}</p>
                <div className="homework-meta">
                    <TimeRemaining dueDate={homework.due_date} />
                    <EstimatedTime minutes={homework.estimated_minutes} />
                </div>
            </div>
            
            <div className="homework-actions">
                <Button 
                    variant="primary"
                    onClick={() => onComplete(homework.id)}
                >
                    شروع کار 🚀
                </Button>
            </div>
        </motion.div>
    );
};
```

### CSS Themes
```css
/* styles/themes/default.css */
:root {
    --primary-color: #3498db;
    --secondary-color: #2ecc71;
    --accent-color: #f39c12;
    --danger-color: #e74c3c;
    --background: #f8f9fa;
    --surface: #ffffff;
    --text-primary: #2c3e50;
    --text-secondary: #7f8c8d;
    
    --border-radius: 12px;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
    --transition: all 0.3s ease;
}

.homework-card {
    background: var(--surface);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: var(--transition);
    border-left: 4px solid var(--primary-color);
}

.homework-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.difficulty-1 { border-left-color: #2ecc71; }
.difficulty-2 { border-left-color: #f39c12; }
.difficulty-3 { border-left-color: #e67e22; }
.difficulty-4 { border-left-color: #e74c3c; }
.difficulty-5 { border-left-color: #9b59b6; }
```

## Mobile-First Design
```css
/* responsive.css */
@media (max-width: 768px) {
    .student-dashboard {
        padding: 1rem;
    }
    
    .homework-card {
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .homework-actions {
        flex-direction: column;
        gap: 0.5rem;
    }
}
```

## Success Metrics
- [ ] Mobile Usability Score > 95%
- [ ] Page Load Speed < 2s
- [ ] User Engagement Time > 20 min/session
- [ ] UI Satisfaction > 4.7/5

---