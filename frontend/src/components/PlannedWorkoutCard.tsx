import type { WorkoutPlan } from '../types';

const quickActions = ['Komoot', 'Strava', 'Garmin'];

export default function PlannedWorkoutCard({ workout }: { workout: WorkoutPlan }) {
  const providerLabel = workout.route_provider?.trim() || 'Route Provider';

  return (
    <section className="card">
      <h3 className="text-lg font-semibold">Planned Workout</h3>
      <p className="text-sm text-slate-300">{workout.date}</p>
      <p className="mt-2 text-sm">Distance: {workout.distanceKm} km</p>
      <p className="text-sm">Elevation: {workout.elevationM} m</p>
      <p className="mt-1 text-xs text-slate-400">
        Route provider: <span className="text-slate-200">{providerLabel}</span>
      </p>

      <div className="mt-3 grid grid-cols-1 gap-2">
        <a
          href={workout.external_url}
          target="_blank"
          rel="noreferrer"
          className="rounded-lg bg-blue-700 px-3 py-2 text-center text-sm text-slate-100"
        >
          Open in {providerLabel}
        </a>

        {quickActions
          .filter((label) => label.toLowerCase() !== providerLabel.toLowerCase())
          .map((label) => (
            <button key={label} className="rounded-lg bg-slate-800 px-3 py-2 text-sm text-slate-100">
              Open in {label}
            </button>
          ))}
      </div>
    </section>
  );
}
