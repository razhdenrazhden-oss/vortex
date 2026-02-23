import type { WorkoutPlan } from '../types';

export default function PlannedWorkoutCard({ workout }: { workout: WorkoutPlan }) {
  return (
    <section className="card">
      <h3 className="text-lg font-semibold">Planned Workout</h3>
      <p className="text-sm text-slate-300">{workout.date}</p>
      <p className="mt-2 text-sm">Distance: {workout.distanceKm} km</p>
      <p className="text-sm">Elevation: {workout.elevationM} m</p>
      <div className="mt-3 grid grid-cols-1 gap-2">
        {['Open in Komoot', 'Open in Strava', 'Send to Garmin'].map((label) => (
          <button key={label} className="rounded-lg bg-slate-800 px-3 py-2 text-sm text-slate-100">
            {label}
          </button>
        ))}
      </div>
    </section>
  );
}
