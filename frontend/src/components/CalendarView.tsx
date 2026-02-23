import { useMemo, useState } from 'react';
import type { WorkoutPlan } from '../types';
import PlannedWorkoutCard from './PlannedWorkoutCard';

const dotColor: Record<WorkoutPlan['workoutType'], string> = {
  endurance: 'bg-blue-400',
  recovery: 'bg-emerald-400',
  interval: 'bg-orange-400',
  race: 'bg-rose-400'
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
              <button
                key={day}
                onClick={() => setSelected(dayWorkout ?? null)}
                className="rounded-lg bg-slate-800 p-2 text-center text-sm"
              >
                <div>{day}</div>
                {dayWorkout ? <div className={`mx-auto mt-1 h-2 w-2 rounded-full ${dotColor[dayWorkout.workoutType]}`} /> : null}
              </button>
            );
          })}
        </div>
      </div>
      {selected && <PlannedWorkoutCard workout={selected} />}
    </section>
  );
}
