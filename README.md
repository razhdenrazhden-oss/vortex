# Activity Load Tracker (MVP Backend)

Минимальный backend-сервис для учёта тренировочной нагрузки.

## Что делает

- Принимает тренировки (`TSS`) через REST.
- Считает дневные метрики:
  - `ATL` (Acute Training Load, tau=7)
  - `CTL` (Chronic Training Load, tau=42)
  - `TSB = CTL - ATL`
  - `readiness_score` в диапазоне 0..100
- Сохраняет тренировки и метрики в PostgreSQL.
- Отдаёт данные через REST API.
- Без авторизации, интеграций и фронтенда.

## Быстрый старт (Docker)

```bash
docker compose up --build
```

API будет доступен на `http://localhost:8000`.

## Локальный запуск (без Docker)

1. Поднимите PostgreSQL (например, в Docker):

```bash
docker run --name activity-db -e POSTGRES_DB=activity_tracker -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
```

2. Установите зависимости и запустите API:

```bash
pip install .
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/activity_tracker
uvicorn app.main:app --reload
```

## API

### Healthcheck

`GET /health`

### Создать тренировку

`POST /workouts`

Пример body:

```json
{
  "workout_date": "2026-01-01",
  "tss": 85
}
```

После добавления пересчитываются дневные метрики начиная с `workout_date` до последнего дня с тренировками, включая дни отдыха (TSS=0).

### Получить метрики

- `GET /metrics`
- `GET /metrics?start_date=2026-01-01&end_date=2026-01-31` (если `start_date > end_date`, API вернёт `400`)
- `GET /metrics/{metric_date}`

## Формулы

Для дня `d` с суммарным `TSS_d`:

- `ATL_d = ATL_{d-1} + (TSS_d - ATL_{d-1}) / 7`
- `CTL_d = CTL_{d-1} + (TSS_d - CTL_{d-1}) / 42`
- `TSB_d = CTL_d - ATL_d`
- `readiness_score` — линейная нормализация `TSB` в диапазон 0..100
  (TSB <= -30 => 0, TSB >= +30 => 100)
