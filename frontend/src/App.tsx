import { useEffect, useMemo, useState } from 'react';
import { fetchDailyStatus, fetchHeartStatus, postManualBiometrics } from './api';
import CalendarView from './components/CalendarView';
import ChartsPanel from './components/ChartsPanel';
import HeartCard from './components/HeartCard';
import ManualEntryModal from './components/ManualEntryModal';
import PlannedWorkoutCard from './components/PlannedWorkoutCard';
import RecommendationCard from './components/RecommendationCard';
import StatusCard from './components/StatusCard';
import { useSwipeTabs } from './hooks/useSwipeTabs';
import type { HeartAlert, LoadPoint, Recommendation, RecommendationType, StatusKind, WeeklyLoad, WorkoutPlan } from './types';

const mockWorkouts: WorkoutPlan[] = [
  {
    id: '1',
    date: '2026-02-03',
    distanceKm: 42,
    elevationM: 480,
    workoutType: 'endurance',
    routes: [
      { route_provider: 'Komoot', external_url: 'https://www.komoot.com/' },
      { route_provider: 'Strava', external_url: 'https://www.strava.com/' },
      { route_provider: 'Garmin', external_url: 'https://connect.garmin.com/' }
    ]
  },
  {
    id: '2',
    date: '2026-02-09',
    distanceKm: 28,
    elevationM: 250,
    workoutType: 'recovery',
    routes: [{ route_provider: 'Strava', external_url: 'https://www.strava.com/' }]
  },
  {
    id: '3',
    date: '2026-02-14',
    distanceKm: 65,
    elevationM: 920,
    workoutType: 'interval',
    routes: [{ route_provider: 'Garmin', external_url: 'https://connect.garmin.com/' }]
  }
];

const mockLoad: LoadPoint[] = Array.from({ length: 10 }).map((_, i) => ({
  date: `D${i + 1}`,
  atl: 55 + i,
  ctl: 48 + i * 0.8,
  tsb: -8 + i,
  state: i > 7 ? 'progress' : 'maintaining'
}));

const mockWeekly: WeeklyLoad[] = [
  { week: 'W1', mileage: 120, calories: 2300, steps: 64000, state: 'progress' },
  { week: 'W2', mileage: 98, calories: 2100, steps: 59000, state: 'maintaining' },
  { week: 'W3', mileage: 140, calories: 2900, steps: 70000, state: 'overreaching' }
];

const mockRecommendations: Recommendation[] = [
  { id: 'r1', type: 'progress', text: 'Progress block: add 1 threshold interval this week.' },
  { id: 'r2', type: 'recovery', text: 'Recovery day tomorrow with easy spin 45 min.' },
  { id: 'r3', type: 'power', text: 'Neuromuscular set: 6x15s seated sprint.' },
  { id: 'r4', type: 'race prep', text: 'Race prep: include one long climb simulation.' }
];

const tabs = ['dashboard', 'calendar', 'charts'] as const;

export default function App() {
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>('dashboard');
  const [manualOpen, setManualOpen] = useState(false);
  const [filter, setFilter] = useState<RecommendationType | 'all'>('all');

  const [formScore, setFormScore] = useState(65);
  const [statusKind, setStatusKind] = useState<StatusKind>('maintaining');
  const [heartSeries, setHeartSeries] = useState<Array<{ date: string; hr: number; hrv: number }>>([
    { date: 'Mon', hr: 58, hrv: 64 },
    { date: 'Tue', hr: 60, hrv: 59 },
    { date: 'Wed', hr: 61, hrv: 56 },
    { date: 'Thu', hr: 63, hrv: 52 },
    { date: 'Fri', hr: 62, hrv: 54 },
    { date: 'Sat', hr: 64, hrv: 50 },
    { date: 'Sun', hr: 62, hrv: 53 }
  ]);

  const userId = 1;

  useEffect(() => {
    const key = 'vortex_last_refresh';
    const now = Date.now();
    const last = Number(localStorage.getItem(key) ?? 0);
    if (now - last < 24 * 60 * 60 * 1000) return;

    Promise.all([fetchDailyStatus(userId), fetchHeartStatus(userId)])
      .then(([status, heart]) => {
        const latest = status.length ? status[status.length - 1] : undefined;
        if (latest) {
          setFormScore(latest.readiness_score);
          setStatusKind(
            latest.tsb >= 5 ? 'progress' : latest.tsb >= -5 ? 'maintaining' : latest.tsb >= -15 ? 'overreaching' : 'detraining'
          );
        }
        setHeartSeries((prev) =>
          prev.map((p, idx) => ({
            ...p,
            hr: heart.avg_hr ? Math.round(heart.avg_hr + (idx - 3) * 0.3) : p.hr,
            hrv: heart.avg_hrv ? Math.round(heart.avg_hrv + (3 - idx) * 0.5) : p.hrv
          }))
        );
        localStorage.setItem(key, String(now));
      })
      .catch(() => undefined);
  }, []);

  const filteredRecommendations = useMemo(
    () => mockRecommendations.filter((r) => (filter === 'all' ? true : r.type === filter)),
    [filter]
  );

  const irregularHeartPattern = heartSeries.some((p) => p.hr > 70 || p.hrv < 45);

  const heartAlert: HeartAlert = {
    show: irregularHeartPattern,
    title: 'Irregular pattern detected',
    message: 'Irregular heart rate pattern detected. Consider medical evaluation if this persists.'
  };

  const tabIndex = tabs.indexOf(activeTab);
  const swipe = useSwipeTabs(
    () => setActiveTab(tabs[Math.min(tabIndex + 1, tabs.length - 1)]),
    () => setActiveTab(tabs[Math.max(tabIndex - 1, 0)])
  );

  return (
    <main className="mx-auto min-h-screen max-w-md space-y-4 p-3" {...swipe}>
      <header className="sticky top-0 z-10 rounded-xl bg-slate-950/85 p-2 backdrop-blur">
        <nav className="grid grid-cols-3 gap-2">
          {tabs.map((t) => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`rounded-lg py-2 text-sm capitalize ${activeTab === t ? 'bg-blue-600' : 'bg-slate-800'}`}
            >
              {t}
            </button>
          ))}
        </nav>
      </header>

      {activeTab === 'dashboard' && (
        <section className="space-y-4">
          <StatusCard score={formScore} status={statusKind} />
          <HeartCard points={heartSeries} irregular={irregularHeartPattern} alert={heartAlert} />

          <div className="card">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-lg font-semibold">Recommendations</h3>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as RecommendationType | 'all')}
                className="rounded bg-slate-800 px-2 py-1 text-xs"
              >
                <option value="all">All</option>
                <option value="progress">Progress</option>
                <option value="recovery">Recovery</option>
                <option value="power">Power</option>
                <option value="race prep">Race Prep</option>
              </select>
            </div>
            <div className="space-y-2">
              {filteredRecommendations.map((r) => (
                <RecommendationCard key={r.id} type={r.type} text={r.text} />
              ))}
            </div>
          </div>

          <PlannedWorkoutCard workout={mockWorkouts[0]} />
        </section>
      )}

      {activeTab === 'calendar' && <CalendarView workouts={mockWorkouts} />}
      {activeTab === 'charts' && <ChartsPanel load={mockLoad} weekly={mockWeekly} />}

      <button
        onClick={() => setManualOpen(true)}
        className="fixed bottom-4 right-4 rounded-full bg-blue-600 px-4 py-3 text-sm font-semibold shadow-xl"
      >
        + Manual Input
      </button>

      <ManualEntryModal
        open={manualOpen}
        onClose={() => setManualOpen(false)}
        onSubmit={async (payload) => {
          await postManualBiometrics({
            user_id: userId,
            entry_date: new Date().toISOString().slice(0, 10),
            hr: payload.hr,
            lactate: payload.lactate,
            power: payload.power
          });
        }}
      />
    </main>
  );
}
