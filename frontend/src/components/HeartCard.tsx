import { Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { HeartAlert } from '../types';

type Point = { date: string; hr: number; hrv: number };

function zoneName(hr: number): string {
  if (hr < 100) return 'Z1 Recovery';
  if (hr < 120) return 'Z2 Endurance';
  if (hr < 140) return 'Z3 Tempo';
  if (hr < 160) return 'Z4 Threshold';
  return 'Z5 VO2+';
}

export default function HeartCard({
  points,
  irregular,
  alert
}: {
  points: Point[];
  irregular: boolean;
  alert?: HeartAlert;
}) {
  const showAlert = alert?.show ?? irregular;
  const alertTitle = alert?.title ?? 'Irregular pattern';
  const alertText = alert?.message ?? 'Irregular heart rate pattern detected. Consider medical evaluation if this persists.';

  return (
    <section className={`card border ${showAlert ? 'border-red-500' : 'border-slate-700'}`}>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Heart Trends</h2>
        <span className="text-xs text-slate-400">HR bpm / HRV ms</span>
      </div>

      {showAlert ? (
        <div className="mb-2 rounded-lg bg-red-950/40 p-2">
          <p className="text-xs font-semibold text-red-300">{alertTitle}</p>
          <p className="text-sm text-red-400">{alertText}</p>
        </div>
      ) : (
        <p className="mb-2 text-sm text-slate-400">HeartAlert placeholder: no heart anomalies detected yet.</p>
      )}

      <div className="mb-2 flex flex-wrap gap-2 text-[11px] text-slate-300">
        <span className="rounded bg-slate-800 px-2 py-1">Z1 &lt; 100 bpm</span>
        <span className="rounded bg-slate-800 px-2 py-1">Z2 100–119 bpm</span>
        <span className="rounded bg-slate-800 px-2 py-1">Z3 120–139 bpm</span>
        <span className="rounded bg-slate-800 px-2 py-1">Z4 140–159 bpm</span>
        <span className="rounded bg-slate-800 px-2 py-1">Z5 160+ bpm</span>
      </div>

      <div className="h-48 w-full">
        <ResponsiveContainer>
          <LineChart data={points}>
            <ReferenceArea y1={100} y2={120} fill="#0ea5e9" fillOpacity={0.08} />
            <ReferenceArea y1={140} y2={160} fill="#f97316" fillOpacity={0.08} />
            <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip
              formatter={(value: number, name: string) => {
                if (name === 'hr') return [`${value} bpm (${zoneName(value)})`, 'HR'];
                return [`${value} ms`, 'HRV'];
              }}
            />
            <Line type="monotone" dataKey="hr" stroke="#f97316" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="hrv" stroke="#22d3ee" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
