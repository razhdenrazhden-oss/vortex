# Activity Load Tracker (MVP Backend)

Минимальный backend-сервис для учёта тренировочной нагрузки, готовый к multi-user SaaS изоляции.

## Что делает

- Поддерживает множественных пользователей (`users`) с изоляцией данных по `user_id`.
- Принимает тренировки (`TSS`) через REST с привязкой к `user_id`.
- Считает дневные метрики (ATL/CTL/TSB/readiness) с непрерывным пересчётом, включая дни отдыха (`TSS=0`).
- Ведёт отдельную таблицу `daily_status` для фронтенда: `status_date`, `user_id`, `readiness_score`, `fatigue_level`, `tsb`.
- Сохраняет биометрию: `hr`, `lactate`, `glucose`, `steps` (все поля optional, хотя бы одно обязательно).
- Отдаёт dashboard и timeline endpoints для frontend.

## Запуск

```bash
pip install .
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/activity_tracker
export DB_SSLMODE=disable
uvicorn app.main:app --reload
```

## Supabase

```bash
export SUPABASE_DB_URL="postgresql+psycopg://postgres.<project_ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres"
export DB_SSLMODE=require
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Приоритет URL подключения:
1. `DATABASE_URL`
2. `SUPABASE_DB_URL`
3. локальный default URL

## API

### Users
- `POST /users`
- `GET /users/{id}`

Пример создания пользователя:
```json
{
  "external_auth_id": "github_12345",
  "subscription_tier": "free",
  "subscription_status": "active"
}
```

> Для `POST /workouts` и `POST /biometrics` пользователь должен существовать.

### Workouts
- `POST /workouts`
- `PUT /workouts/{workout_id}`
- `DELETE /workouts/{workout_id}`
- `GET /workouts?user_id=1&start=2026-01-01&end=2026-01-31`

`POST /workouts`:
```json
{
  "user_id": 1,
  "workout_date": "2026-01-01",
  "tss": 85
}
```

### Metrics
- `GET /metrics?user_id=1`
- `GET /metrics?user_id=1&start_date=2026-01-01&end_date=2026-01-31`
- `GET /metrics/{metric_date}?user_id=1`

### Daily status
- `GET /daily-status?user_id=1`
- `GET /daily-status?user_id=1&start=2026-01-01&end=2026-01-31`

### Heart status
- `GET /users/{id}/heart-status`

Возвращает user-scoped кардио-статус за последнюю дату: `avg_hr`, `avg_hrv`, `cardio_risk_level`, `recommendations`.

### Dashboard
- `GET /users/{id}/dashboard`

Возвращает последние user-scoped данные: workout, metric, daily_status, biometrics.

### Heart & Cardiovascular Analytics (optional)
- `GET /users/{id}/cardio-analytics?days=14`

Возвращает cardio score, risk level и рекомендации на основе дневного статуса и последних биометрических данных.

При добавлении/обновлении/удалении тренировки статусы и метрики пересчитываются в user-scope с учётом rest days.

### Biometrics
- `POST /biometrics`

```json
{
  "user_id": 1,
  "entry_date": "2026-01-01",
  "hr": 52,
  "hrv": 58,
  "lactate": 1.8,
  "glucose": 95,
  "steps": 10500
}
```

## Формулы

- `ATL_d = ATL_{d-1} + (TSS_d - ATL_{d-1}) / 7`
- `CTL_d = CTL_{d-1} + (TSS_d - CTL_{d-1}) / 42`
- `TSB_d = CTL_d - ATL_d`
- `readiness_score` — нормализация `TSB` в диапазон `0..100`
- `fatigue_level`:
  - `high`, если `TSB <= -20`
  - `moderate`, если `-20 < TSB <= -5`
  - `low`, если `TSB > -5`


## External Integrations MVP (Strava / Intervals / GPX)

Added backend skeleton endpoints for ingestion + frontend-ready form data:

- `GET /auth/strava` – returns OAuth2 authorization URL
- `GET /auth/strava/callback?code=...` – OAuth2 code exchange skeleton and token storage
- `POST /auth/intervals` – save Intervals.icu API token
- `GET /user/activities?start_date=&end_date=` – user activities in normalized units
- `GET /user/form` – ATL/CTL/TSB yearly series for charts (`date, atl, ctl, tsb, load_state`)
- `POST /user/upload-gpx` – GPX upload/import skeleton
- `POST /internal/sync-daily` – cron-style daily recompute trigger

Auth model:
- Endpoints require bearer token (Supabase JWT via `SUPABASE_JWT_SECRET`).
- Dev fallback supported: `Authorization: Bearer dev-<external_auth_id>`.

Normalized units:
- HR: bpm
- Power: watts
- Distance: km
- Duration: min

Load-state colors for frontend:
- `overreaching` (orange)
- `progress` (green)
- `maintaining` (blue)
- `detraining` (gray)


## Render Deployment (FastAPI Web Service)

### 1) Create Web Service on Render
- **Type:** Web Service
- **Runtime:** Python
- **Python version:** `3.11`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Repository already contains ready-to-use Render config: **`.render.yaml`**.

### 2) Required Environment Variables (Render Dashboard)
Add these in **Render → Service → Environment**:

- `SUPABASE_URL` = `<your-supabase-url>`
- `SUPABASE_ANON_KEY` = `<your-supabase-anon-key>`
- `SUPABASE_JWT_SECRET` = `<your-supabase-jwt-secret>`
- `DATABASE_URL` = `<supabase-postgres-connection-url>`
- `DB_SSLMODE` = `require`
- `STRAVA_CLIENT_ID` = `<strava-client-id>`
- `STRAVA_CLIENT_SECRET` = `<strava-client-secret>`
- `STRAVA_REDIRECT_URI` = `https://<your-render-domain>/auth/strava/callback`
- `INTERVALS_API_TOKEN` = `<intervals-api-token>`

> В репозитории не храните реальные ключи. Только placeholders.

### 3) Deploy via Codex
1. Commit & push changes (including `.render.yaml` and `requirements.txt`).
2. In Render choose **New + → Blueprint** and select this repo.
3. Render прочитает `.render.yaml` и создаст web service автоматически.
4. Заполните env vars в Render UI (или через Render API).
5. Запустите deploy.

### 4) Daily refresh (optional cron)
- В `.render.yaml` добавлен пример `cronJobs` для ежедневного обновления.
- Cron вызывает `POST /update-data`, который запускает дневной sync/recompute.
- Если endpoint закрыт сетью, используйте внутренний cron worker или private network call.

### 5) Post-deploy API checks
Проверка health:
```bash
curl https://<your-render-domain>/health
```

Проверка OAuth start URL:
```bash
curl -H "Authorization: Bearer <supabase-jwt-or-dev-token>"   https://<your-render-domain>/auth/strava
```

Проверка активностей пользователя:
```bash
curl -H "Authorization: Bearer <supabase-jwt-or-dev-token>"   "https://<your-render-domain>/user/activities?start_date=2026-01-01&end_date=2026-12-31"
```

Проверка form-series для графика:
```bash
curl -H "Authorization: Bearer <supabase-jwt-or-dev-token>"   https://<your-render-domain>/user/form
```

Проверка daily update endpoint:
```bash
curl -X POST https://<your-render-domain>/update-data
```
