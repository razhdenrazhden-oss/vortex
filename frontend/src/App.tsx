import { useEffect, useMemo, useState } from 'react';
import { fetchDailyStatus, fetchHeartStatus, fetchUserActivities, fetchUserForm, postManualBiometrics } from './api';
import CalendarView from './components/CalendarView';
import ChartsPanel from './components/ChartsPanel';
import HeartCard from './components/HeartCard';
import ManualEntryModal from './components/ManualEntryModal';
import PlannedWorkoutCard from './components/PlannedWorkoutCard';
import RecommendationCard from './components/RecommendationCard';
import StatusCard from './components/StatusCard';
import { useSwipeTabs } from './hooks/useSwipeTabs';
import type { ActivityItem, HeartAlert, LoadPoint, Recommendation, RecommendationType, StatusKind, WeeklyLoad, WorkoutPlan } from './types';

const mockWorkouts: WorkoutPlan[] = [
  { id: '1', date: '2026-02-20', distanceKm: 68, durationMin: 150, avgHr: 142, avgPower: 210, elevationM: 840, workoutType: 'endurance', color: '#22c55e', polyline: null, routes: [{ route_provider: 'Strava', external_url: 'https://www.strava.com/' }] }
];

const mockLoad: LoadPoint[] = [
  { date: 'Mon', atl: 50, ctl: 70, tsb: 20, state: 'progress', color: '#22c55e' },
  { date: 'Tue', atl: 55, ctl: 71, tsb: 16, state: 'maintaining', color: '#3b82f6' },
  { date: 'Wed', atl: 62, ctl: 72, tsb: 10, state: 'maintaining', color: '#3b82f6' }
];

const mockWeekly: WeeklyLoad[] = [
  { week: 'W1', mileage: 210, calories: 3900, steps: 63000, state: 'progress' },
  { week: 'W2', mileage: 180, calories: 3500, steps: 60000, state: 'maintaining' }
];

const mockRecommendations: Recommendation[] = [
  { id: 'r1', type: 'progress', text: 'Solid adaptation. Add one tempo block.' },
  { id: 'r2', type: 'recovery', text: 'Keep tomorrow easy with Z1 spin.' },
  { id: 'r3', type: 'power', text: 'Include 6x30s seated sprint.' },
  { id: 'r4', type: 'race prep', text: 'Race prep: include one long climb simulation.' }
];

const tabs = ['dashboard', 'calendar', 'charts'] as const;

export default function App() {
  const [activeTab, setActiveTab] = useState<(typeof tabs)[number]>('dashboard');
  const [manualOpen, setManualOpen] = useState(false);
  const [filter, setFilter] = useState<RecommendationType | 'all'>('all');

  const [formScore, setFormScore] = useState(65);
  const [statusKind, setStatusKind] = useState<StatusKind>('maintaining');
  const [workouts, setWorkouts] = useState<WorkoutPlan[]>(mockWorkouts);
  const [load, setLoad] = useState<LoadPoint[]>(mockLoad);
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

    Promise.all([fetchDailyStatus(userId), fetchHeartStatus(userId), fetchUserActivities(), fetchUserForm()])
      .then(([status, heart, activities, form]) => {
        const latest = status.length ? status[status.length - 1] : undefined;
        if (latest) {
          setFormScore(latest.readiness_score);
          setStatusKind(latest.tsb >= 5 ? 'progress' : latest.tsb >= -5 ? 'maintaining' : latest.tsb >= -15 ? 'overreaching' : 'detraining');
        }
        if (activities.length) {
          setWorkouts(
            activities.map((a: ActivityItem, idx) => ({
              id: `${a.source}-${idx}`,
              date: a.date,
              distanceKm: a.distance_km,
              durationMin: a.duration_min,
              avgHr: a.hr_bpm,
              avgPower: a.power_w,
              elevationM: a.elevation_m ?? 0,
              workoutType: a.power_w && a.power_w > 250 ? 'interval' : a.distance_km >= 70 ? 'endurance' : 'recovery',
              color: a.color ?? '#3b82f6',
              polyline: a.route.polyline,
              routes: a.route.url ? [{ route_provider: a.source, external_url: a.route.url }] : []
            }))
          );
        }
        if (form.length) setLoad(form);
        setHeartSeries((prev) => prev.map((p, idx) => ({ ...p, hr: heart.avg_hr ? Math.round(heart.avg_hr + (idx - 3) * 0.3) : p.hr, hrv: heart.avg_hrv ? Math.round(heart.avg_hrv + (3 - idx) * 0.5) : p.hrv })));
        localStorage.setItem(key, String(now));
      })
      .catch(() => undefined);
  }, []);

  const filteredRecommendations = useMemo(() => mockRecommendations.filter((r) => (filter === 'all' ? true : r.type === filter)), [filter]);

  const irregularHeartPattern = heartSeries.some((p) => p.hr > 70 || p.hrv < 45);
  const heartAlert: HeartAlert = {
    show: irregularHeartPattern,
    title: 'Irregular pattern detected',
    message: 'Irregular heart rate pattern detected. Consider medical evaluation if this persists.'
  };

  const tabIndex = tabs.indexOf(activeTab);
  const swipe = useSwipeTabs(() => setActiveTab(tabs[Math.min(tabIndex + 1, tabs.length - 1)]), () => setActiveTab(tabs[Math.max(tabIndex - 1, 0)]));

  return (
    <main className="mx-auto min-h-screen max-w-md space-y-4 p-3" {...swipe}>
      <header className="sticky top-0 z-10 rounded-xl bg-slate-950/85 p-2 backdrop-blur">
        <nav className="grid grid-cols-3 gap-2">
          {tabs.map((t) => (
            <button key={t} onClick={() => setActiveTab(t)} className={`rounded-lg py-2 text-sm capitalize ${activeTab === t ? 'bg-blue-600' : 'bg-slate-800'}`}>
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
              <select value={filter} onChange={(e) => setFilter(e.target.value as RecommendationType | 'all')} className="rounded bg-slate-800 px-2 py-1 text-xs">
                <option value="all">All</option>
                <option value="progress">Progress</option>
                <option value="recovery">Recovery</option>
                <option value="power">Power</option>
                <option value="race prep">Race Prep</option>
              </select>
            </div>
            <div className="space-y-2">{filteredRecommendations.map((r) => <RecommendationCard key={r.id} type={r.type} text={r.text} />)}</div>
          </div>

          {workouts[0] && <PlannedWorkoutCard workout={workouts[0]} />}
        </section>
      )}

      {activeTab === 'calendar' && <CalendarView workouts={workouts} />}
      {activeTab === 'charts' && <ChartsPanel load={load} weekly={mockWeekly} />}

      <button onClick={() => setManualOpen(true)} className="fixed bottom-4 right-4 rounded-full bg-blue-600 px-4 py-3 text-sm font-semibold shadow-xl">
        + Manual Input
      </button>

      <ManualEntryModal
        open={manualOpen}
        onClose={() => setManualOpen(false)}
        onSubmit={async (payload) => {
          await postManualBiometrics({ user_id: userId, entry_date: new Date().toISOString().slice(0, 10), hr: payload.hr, lactate: payload.lactate, power: payload.power });
        }}
      />
    </main>
  );
}
