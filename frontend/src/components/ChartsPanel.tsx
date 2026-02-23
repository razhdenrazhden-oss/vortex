import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { LoadPoint, WeeklyLoad } from '../types';

const stateColor: Record<LoadPoint['state'], string> = {
  progress: '#22c55e',
  maintaining: '#3b82f6',
  overreaching: '#f97316',
  detraining: '#9ca3af'
};

export default function ChartsPanel({ load, weekly }: { load: LoadPoint[]; weekly: WeeklyLoad[] }) {
  return (
    <section className="space-y-4">
      <div className="card h-64">
        <h3 className="mb-1 text-lg font-semibold">ATL / CTL / TSB</h3>
        <p className="mb-2 text-xs text-slate-400">Units: load points (TSS-derived)</p>
        <ResponsiveContainer>
          <LineChart data={load}>
            <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip
              formatter={(value: number, name: string) => [`${value.toFixed?.(1) ?? value} pts`, name.toUpperCase()]}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line type="monotone" dataKey="atl" stroke="#f97316" dot={false} />
            <Line type="monotone" dataKey="ctl" stroke="#22c55e" dot={false} />
            <Line type="monotone" dataKey="tsb" stroke="#3b82f6" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card h-72">
        <h3 className="mb-1 text-lg font-semibold">Weekly Load Mix</h3>
        <p className="mb-2 text-xs text-slate-400">Mileage: km, Calories: kcal, Steps: count</p>
        <ResponsiveContainer>
          <BarChart data={weekly}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="4 4" />
            <XAxis dataKey="week" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip
              formatter={(value: number, name: string) => {
                if (name === 'mileage') return [`${value} km`, 'Mileage'];
                if (name === 'calories') return [`${value} kcal`, 'Calories'];
                return [`${value}`, 'Steps'];
              }}
            />
            <Bar dataKey="mileage" fill="#22c55e" />
            <Bar dataKey="calories" fill="#f97316" />
            <Bar dataKey="steps" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-2 flex flex-wrap gap-2 text-[11px] text-slate-300">
          {Object.entries(stateColor).map(([state, color]) => (
            <span key={state} className="inline-flex items-center gap-1 rounded bg-slate-800 px-2 py-1 capitalize">
              <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
              {state}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
