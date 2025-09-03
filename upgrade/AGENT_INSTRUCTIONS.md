# دستورالعمل Agent‌ها
## Instructions for Multiple Agents Implementation

### نحوه کار با این مستندات

#### برای Agent Base:
1. **شروع از**: `phases/phase-1-base/README.md`
2. **فایل‌های کلیدی**: 
   - `models.py` - کپی به `educational/models.py`
   - `serializers.py` - کپی به `educational/serializers.py`
   - `views.py` - کپی به `educational/views.py`
   - `tests.py` - کپی به `educational/tests.py`
3. **مراحل اجرا**:
   ```bash
   python manage.py startapp educational
   # کپی فایل‌ها
   python manage.py makemigrations
   python manage.py migrate
   python manage.py test
   ```

#### برای Agent Core:
1. **پیش‌نیاز**: Phase 1 تکمیل شده
2. **شروع از**: `phases/phase-2-core/README.md`  
3. **تمرکز**: AI integration, Gamification, Question Bank
4. **فایل‌های جدید**: AI services, Advanced models, Celery tasks

#### برای Agent Parent:
1. **پیش‌نیاز**: Phases 1-2 تکمیل شده
2. **شروع از**: `phases/phase-3-parent/README.md`
3. **تمرکز**: Parental controls, Monitoring, Notifications
4. **فایل‌های جدید**: Parent models, Control middleware, Report system

#### برای Agent AI:
1. **پیش‌نیاز**: Phases 1-3 تکمیل شده
2. **شروع از**: `phases/phase-4-ai/README.md`
3. **تمرکز**: Advanced AI, Adaptive learning, Personalization

#### برای Agent UI:
1. **پیش‌نیاز**: Phases 1-4 تکمیل شده
2. **شروع از**: `phases/phase-5-ui/README.md`
3. **تمرکز**: Frontend, Animations, Mobile-first design

#### برای Agent Ops:
1. **پیش‌نیاز**: Phases 1-5 تکمیل شده
2. **شروع از**: `phases/phase-6-ops/README.md`
3. **تمرکز**: Production deployment, Monitoring, Security

## قوانین کلی

### 1. Git Workflow
```bash
# هر agent باید:
git checkout feature/educational-upgrade
git checkout -b phase-{N}-{agent-name}
# کار روی فاز
git add .
git commit -m "feat(phase-{N}): implement {feature}"
git push origin phase-{N}-{agent-name}
# ایجاد PR
```

### 2. Testing Requirements
- **Unit Tests**: 80%+ coverage
- **Integration Tests**: تمام API endpoints
- **Performance Tests**: < 2s response time
- **Security Tests**: validation و access control

### 3. Code Quality
- **Type Hints**: همه functions
- **Docstrings**: کلاس‌ها و methods مهم
- **PEP8**: استاندارد Python
- **Persian Comments**: برای بخش‌های پیچیده

### 4. Documentation
- **README**: هر فاز مستندات کامل دارد
- **API Docs**: Swagger/OpenAPI
- **Code Comments**: فارسی برای وضوح
- **Deployment Guides**: step-by-step

## نکات مهم

### امنیت کودکان
- همیشه Content Safety Filter فعال
- Parental Control در تمام endpoints
- Data Privacy مطابق GDPR
- No Personal Information Storage

### عملکرد
- Database Indexing
- Redis Caching  
- API Rate Limiting
- Mobile Optimization

### کیفیت کد
- Clean Architecture
- SOLID Principles
- DRY (Don't Repeat Yourself)
- Test-Driven Development

---

**هر Agent باید این دستورالعمل را دقیقاً دنبال کند.**