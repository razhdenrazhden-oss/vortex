import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { LoadPoint, WeeklyLoad } from '../types';

export default function ChartsPanel({ load, weekly }: { load: LoadPoint[]; weekly: WeeklyLoad[] }) {
  return (
    <section className="space-y-4">
      <div className="card h-60">
        <h3 className="mb-2 text-lg font-semibold">ATL / CTL / TSB</h3>
        <ResponsiveContainer>
          <LineChart data={load}>
            <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="atl" stroke="#f97316" dot={false} />
            <Line type="monotone" dataKey="ctl" stroke="#22c55e" dot={false} />
            <Line type="monotone" dataKey="tsb" stroke="#3b82f6" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card h-72">
        <h3 className="mb-2 text-lg font-semibold">Weekly load / calories / steps</h3>
        <ResponsiveContainer>
          <BarChart data={weekly}>
            <CartesianGrid stroke="#1e293b" strokeDasharray="4 4" />
            <XAxis dataKey="week" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="mileage" fill="#22c55e" />
            <Bar dataKey="calories" fill="#f97316" />
            <Bar dataKey="steps" fill="#3b82f6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
