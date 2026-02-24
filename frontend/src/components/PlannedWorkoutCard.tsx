import type { WorkoutPlan } from '../types';

const preferredProviders = ['Komoot', 'Strava', 'Garmin'];

export default function PlannedWorkoutCard({ workout }: { workout: WorkoutPlan }) {
  const routesByProvider = new Map(workout.routes.map((r) => [r.route_provider.toLowerCase(), r.external_url]));

  return (
    <section className="card">
      <h3 className="text-lg font-semibold">Planned Workout</h3>
      <p className="text-sm text-slate-300">{workout.date}</p>
      <p className="mt-2 text-sm">Distance: {workout.distanceKm} km</p>
      <p className="text-sm">Elevation: {workout.elevationM} m</p>

      <div className="mt-2 rounded-lg bg-slate-800/70 p-2">
        <p className="mb-1 text-xs uppercase tracking-wide text-slate-400">Routes</p>
        <ul className="space-y-1 text-xs text-slate-200">
          {workout.routes.map((route, idx) => (
            <li key={`${route.route_provider}-${idx}`} className="flex items-center justify-between gap-2">
              <span>{route.route_provider}</span>
              <a href={route.external_url} target="_blank" rel="noreferrer" className="text-blue-300 underline">
                external_url
              </a>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-3 grid grid-cols-1 gap-2">
        {preferredProviders.map((provider) => {
          const url = routesByProvider.get(provider.toLowerCase());
          return url ? (
            <a
              key={provider}
              href={url}
              target="_blank"
              rel="noreferrer"
              className="rounded-lg bg-slate-800 px-3 py-2 text-center text-sm text-slate-100"
            >
              Open in {provider}
            </a>
          ) : (
            <button key={provider} disabled className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-slate-500">
              Open in {provider}
            </button>
          );
        })}
      </div>
    </section>
  );
}
