import type { StatusKind } from '../types';

const statusColor: Record<StatusKind, string> = {
  progress: 'border-l-progress',
  maintaining: 'border-l-maintaining',
  overreaching: 'border-l-overreaching',
  detraining: 'border-l-detraining'
};

export default function StatusCard({ score, status }: { score: number; status: StatusKind }) {
  return (
    <section className={`card border-l-4 ${statusColor[status]}`}>
      <p className="text-sm text-slate-400">Form Status</p>
      <h1 className="text-4xl font-bold">{Math.round(score)}</h1>
      <p className="mt-1 text-sm capitalize text-slate-300">{status}</p>
    </section>
  );
}
