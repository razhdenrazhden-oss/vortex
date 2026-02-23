import { useMemo, useState } from 'react';
import type { WorkoutPlan } from '../types';
import MiniRouteMap from './MiniRouteMap';
import PlannedWorkoutCard from './PlannedWorkoutCard';

const dotColor: Record<string, string> = {
  '#f97316': 'bg-orange-400',
  '#22c55e': 'bg-green-400',
  '#3b82f6': 'bg-blue-400',
  '#9ca3af': 'bg-slate-400'
};

export default function CalendarView({ workouts }: { workouts: WorkoutPlan[] }) {
  const [selected, setSelected] = useState<WorkoutPlan | null>(null);
  const days = useMemo(() => Array.from({ length: 30 }, (_, i) => i + 1), []);

  return (
    <section className="space-y-4">
      <div className="card">
        <h3 className="mb-3 text-lg font-semibold">Calendar</h3>
        <div className="grid grid-cols-7 gap-2">
          {days.map((day) => {
            const dayWorkout = workouts.find((w) => Number(w.date.slice(-2)) === day);
            return (
              <button key={day} onClick={() => setSelected(dayWorkout ?? null)} className="rounded-lg bg-slate-800 p-2 text-center text-sm">
                <div>{day}</div>
                {dayWorkout ? <div className={`mx-auto mt-1 h-2 w-2 rounded-full ${dotColor[dayWorkout.color ?? ''] ?? 'bg-slate-500'}`} /> : null}
              </button>
            );
          })}
        </div>
      </div>
      {selected && (
        <div className="card">
          <PlannedWorkoutCard workout={selected} />
          <MiniRouteMap polyline={selected.polyline} />
          <div className="mt-2 text-xs text-slate-300">
            <p>Date: {selected.date}</p>
            <p>Distance: {selected.distanceKm} km</p>
            <p>Duration: {selected.durationMin ?? '-'} min</p>
            <p>Avg HR: {selected.avgHr ?? '-'} bpm</p>
            <p>Avg Power: {selected.avgPower ?? '-'} W</p>
          </div>
        </div>
      )}
    </section>
  );
}
