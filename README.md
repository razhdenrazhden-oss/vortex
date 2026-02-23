# Activity Load Tracker (MVP Backend)

Минимальный backend-сервис для учёта тренировочной нагрузки.

## Что делает

- Принимает тренировки (`TSS`) через REST с привязкой к `user_id`.
- Считает дневные метрики:
  - `ATL` (Acute Training Load, tau=7)
  - `CTL` (Chronic Training Load, tau=42)
  - `TSB = CTL - ATL`
  - `readiness_score` в диапазоне 0..100
- Заполняет отдельную таблицу `daily_status` для фронтенда:
  - `status_date`, `user_id`, `readiness_score`, `fatigue_level`, `tsb`
- Сохраняет тренировки, метрики и биометрию в PostgreSQL.
- Отдаёт данные через REST API.
- Без авторизации и внешних интеграций.

## Быстрый старт (Docker)

```bash
docker compose up --build
```

API будет доступен на `http://localhost:8000`.

## Локальный запуск (без Docker)

```bash
pip install .
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/activity_tracker
uvicorn app.main:app --reload
```

## API

### Healthcheck

- `GET /health`

### Workouts

- `POST /workouts`
- `GET /workouts?user_id=1&start=2026-01-01&end=2026-01-31`

`POST /workouts` пример:

```json
{
  "user_id": 1,
  "workout_date": "2026-01-01",
  "tss": 85
}
```

После добавления тренировки пересчитываются дневные метрики и daily status только для этого `user_id`, включая дни отдыха (TSS=0).

### Metrics

- `GET /metrics?user_id=1`
- `GET /metrics?user_id=1&start_date=2026-01-01&end_date=2026-01-31`
- `GET /metrics/{metric_date}?user_id=1`

### Daily status

- `GET /daily-status?user_id=1`
- `GET /daily-status?user_id=1&start=2026-01-01&end=2026-01-31`

### Dashboard

- `GET /users/{id}/dashboard`

Возвращает последний workout, последнюю метрику и текущий статус готовности пользователя.

### Biometrics

- `POST /biometrics`

Пример:

```json
{
  "user_id": 1,
  "entry_date": "2026-01-01",
  "resting_hr": 52,
  "hrv": 68,
  "body_weight": 73.4
}
```

## Формулы

Для дня `d` с суммарным `TSS_d`:

- `ATL_d = ATL_{d-1} + (TSS_d - ATL_{d-1}) / 7`
- `CTL_d = CTL_{d-1} + (TSS_d - CTL_{d-1}) / 42`
- `TSB_d = CTL_d - ATL_d`
- `readiness_score` — линейная нормализация `TSB` в диапазон 0..100
  (TSB <= -30 => 0, TSB >= +30 => 100)
- `fatigue_level` на основе `TSB`:
  - `high`, если `TSB <= -20`
  - `moderate`, если `-20 < TSB <= -5`
  - `low`, если `TSB > -5`
