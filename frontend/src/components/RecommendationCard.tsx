import type { RecommendationType } from '../types';

const recColor: Record<RecommendationType, string> = {
  progress: 'border-l-progress',
  recovery: 'border-l-recovery',
  power: 'border-l-power',
  'race prep': 'border-l-raceprep'
};

export default function RecommendationCard({
  type,
  text
}: {
  type: RecommendationType;
  text: string;
}) {
  return (
    <article className={`card border-l-4 ${recColor[type]}`}>
      <p className="text-xs uppercase tracking-wide text-slate-400">{type}</p>
      <p className="mt-1 text-sm text-slate-100">{text}</p>
    </article>
  );
}
