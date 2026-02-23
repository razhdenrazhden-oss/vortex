import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

type Point = { date: string; hr: number; hrv: number };

export default function HeartCard({ points, irregular }: { points: Point[]; irregular: boolean }) {
  return (
    <section className={`card border ${irregular ? 'border-red-500' : 'border-slate-700'}`}>
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Heart Trends</h2>
        {irregular && <span className="text-xs text-red-400">Irregular pattern</span>}
      </div>
      {irregular && (
        <p className="mb-2 text-sm text-red-400">Consider medical evaluation if this persists</p>
      )}
      <div className="h-48 w-full">
        <ResponsiveContainer>
          <LineChart data={points}>
            <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="hr" stroke="#f97316" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="hrv" stroke="#22d3ee" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
