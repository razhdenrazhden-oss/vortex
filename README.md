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

### Dashboard
- `GET /users/{id}/dashboard`

Возвращает последние user-scoped данные: workout, metric, daily_status, biometrics.

При добавлении/обновлении/удалении тренировки статусы и метрики пересчитываются в user-scope с учётом rest days.

### Biometrics
- `POST /biometrics`

```json
{
  "user_id": 1,
  "entry_date": "2026-01-01",
  "hr": 52,
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
