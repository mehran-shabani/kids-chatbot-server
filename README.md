# Kids Chatbot Server (Django + DRF)

Backend for a kids-friendly chatbot with OTP login (Kavenegar), JWT, wallet/subscription, OpenAI models with custom API base, memory summaries via Celery, Postgres + Redis (Docker).

## Quickstart (Docker)

```bash
cp .env.example .env
docker compose up --build
# After boot:
# Open OpenAPI schema
# http://localhost:8000/api/schema/
# Swagger UI
# http://localhost:8000/api/docs/
```

## Quickstart (Local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env.example | xargs) || true
python manage.py migrate
python manage.py runserver
```

## Seed Model Catalog

```bash
python manage.py seed_models
```

## Key Endpoints

- POST `/api/accounts/register-login`
- POST `/api/accounts/verify-otp`
- POST `/api/accounts/complete-profile`
- GET  `/api/billing/wallet`
- POST `/api/billing/purchase` (dev/mock)
- GET  `/api/models`
- POST `/api/chat/send`

## Celery

In Docker, `worker` and `beat` services are included. Beat schedules run at 00:00 and 00:30 Tehran local time.

## Tests

```bash
pytest
```

## Notes

- Default auth: JWT (Session auth also enabled for local/dev convenience).
- Timezone: Asia/Tehran. Celery uses local timezone (UTC disabled) to align crontab.
- Wallet unit: tokens. 1M top-up price uses `DEFAULT_MILLION_TOKENS_PRICE_USD` with `PROFIT_MARGIN`.