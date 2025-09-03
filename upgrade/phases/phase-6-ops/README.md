# Phase 6: Operations & Production
## فاز 6: عملیات و آماده‌سازی تولید (Agent Ops)

**مدت**: 2 هفته | **Agent**: Ops Agent | **وابستگی**: Phases 1-5

## اهداف

### هدف اصلی
آماده‌سازی سیستم برای عرضه عمومی و مقیاس‌پذیری

### ویژگی‌های کلیدی
1. **Monitoring & Logging**: نظارت کامل سیستم
2. **Performance Optimization**: بهینه‌سازی عملکرد
3. **Security Hardening**: تقویت امنیت
4. **Scalability**: آمادگی برای رشد
5. **Deployment Automation**: خودکارسازی استقرار

## Infrastructure

### Docker Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  web:
    image: educational-chatbot:latest
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - EDUCATIONAL_MODE=true
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=educational_chatbot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Monitoring Stack
```yaml
# monitoring/docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    
  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
    
  promtail:
    image: grafana/promtail
    volumes:
      - /var/log:/var/log:ro
      - ./promtail.yml:/etc/promtail/config.yml
```

## Performance Optimization

### Database Optimization
```python
# educational/optimizations.py
class DatabaseOptimizer:
    """بهینه‌سازی پایگاه داده"""
    
    @staticmethod
    def create_indexes():
        """ایجاد ایندکس‌های مورد نیاز"""
        indexes = [
            "CREATE INDEX CONCURRENTLY idx_homework_student_status ON educational_homework(student_id, status);",
            "CREATE INDEX CONCURRENTLY idx_homework_due_date ON educational_homework(due_date) WHERE status IN ('pending', 'in_progress');",
            "CREATE INDEX CONCURRENTLY idx_daily_activity_date ON educational_dailyactivity(student_id, date);",
            "CREATE INDEX CONCURRENTLY idx_questions_subject_grade ON educational_question(subject_id, grade_level, difficulty);",
        ]
        
        from django.db import connection
        with connection.cursor() as cursor:
            for index_sql in indexes:
                cursor.execute(index_sql)
    
    @staticmethod
    def optimize_queries():
        """بهینه‌سازی کوئری‌ها"""
        # استفاده از select_related و prefetch_related
        # Cache کردن کوئری‌های پرتکرار
        pass

# Cache Strategy
CACHE_SETTINGS = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'educational',
        'TIMEOUT': 300,
    }
}
```

### Security Hardening
```python
# security/settings.py
SECURITY_SETTINGS = {
    # Rate Limiting
    'RATELIMIT_ENABLE': True,
    'RATELIMIT_USE_CACHE': 'default',
    
    # Content Security Policy
    'CSP_DEFAULT_SRC': ["'self'"],
    'CSP_SCRIPT_SRC': ["'self'", "'unsafe-inline'"],
    'CSP_STYLE_SRC': ["'self'", "'unsafe-inline'"],
    
    # Child Safety
    'CHILD_PROTECTION_ENABLED': True,
    'CONTENT_MODERATION_LEVEL': 'strict',
    'PARENTAL_OVERSIGHT': True,
    
    # Data Protection
    'GDPR_COMPLIANCE': True,
    'DATA_RETENTION_DAYS': 365,
    'PERSONAL_DATA_ENCRYPTION': True,
}
```

## Deployment Scripts

### Kubernetes Deployment
```yaml
# k8s/educational-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: educational-chatbot
  labels:
    app: educational-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: educational-chatbot
  template:
    metadata:
      labels:
        app: educational-chatbot
    spec:
      containers:
      - name: web
        image: educational-chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "config.settings.production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Monitoring & Alerting

### Health Checks
```python
# educational/health.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    """بررسی سلامت سیستم"""
    checks = {
        'database': _check_database(),
        'cache': _check_cache(),
        'ai_service': _check_ai_service(),
        'storage': _check_storage(),
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JsonResponse({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'checks': checks,
        'timestamp': timezone.now().isoformat()
    }, status=status_code)

def _check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except:
        return False

def _check_cache():
    try:
        cache.set('health_check', 'ok', 10)
        return cache.get('health_check') == 'ok'
    except:
        return False
```

## Success Metrics
- [ ] System Uptime > 99.5%
- [ ] Response Time < 2s (95th percentile)
- [ ] Error Rate < 0.1%
- [ ] Mobile Performance Score > 90

---

**فاز نهایی برای آماده‌سازی تولید.**