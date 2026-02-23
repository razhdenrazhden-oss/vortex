# Vortex Frontend (React + TypeScript + Tailwind + PWA)

## Run

```bash
cd frontend
npm install
npm run dev
```

Set API URL if needed:

```bash
export VITE_API_URL=http://localhost:8000
```

## Structure

- `src/components/StatusCard.tsx`
- `src/components/HeartCard.tsx`
- `src/components/RecommendationCard.tsx`
- `src/components/PlannedWorkoutCard.tsx`
- `src/components/CalendarView.tsx`
- `src/components/ChartsPanel.tsx`
- `src/components/ManualEntryModal.tsx`


## Notes
- `PlannedWorkoutCard` supports `route_provider` + `external_url` for extensible routing services.
- `HeartCard` includes HR zone legend/tooltips and a HeartAlert placeholder when no critical data is present.
- Charts include unit hints for consistency (pts/km/kcal/steps).
