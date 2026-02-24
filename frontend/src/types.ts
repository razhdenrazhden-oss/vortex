export type StatusKind = 'progress' | 'maintaining' | 'overreaching' | 'detraining';
export type RecommendationType = 'progress' | 'recovery' | 'power' | 'race prep';

export interface DailyStatus {
  status_date: string;
  readiness_score: number;
  fatigue_level: string;
  tsb: number;
}

export interface HeartStatus {
  metric_date: string;
  avg_hr: number | null;
  avg_hrv: number | null;
  cardio_risk_level: 'Normal' | 'Slight Risk' | 'High Risk';
  recommendations: string[];
}

export interface HeartAlert {
  show: boolean;
  title: string;
  message: string;
}

export interface WorkoutRoute {
  route_provider: string;
  external_url: string;
}

export interface ActivityItem {
  date: string;
  source: string;
  hr_bpm: number | null;
  power_w: number | null;
  distance_km: number;
  duration_min: number;
  elevation_m: number | null;
  atl: number | null;
  ctl: number | null;
  tsb: number | null;
  color: string | null;
  route: { url: string | null; polyline: string | null };
}

export interface WorkoutPlan {
  id: string;
  date: string;
  distanceKm: number;
  durationMin?: number;
  avgHr?: number | null;
  avgPower?: number | null;
  elevationM: number;
  workoutType: 'endurance' | 'recovery' | 'interval' | 'race';
  color?: string;
  polyline?: string | null;
  routes: WorkoutRoute[];
}

export interface Recommendation {
  id: string;
  type: RecommendationType;
  text: string;
}

export interface LoadPoint {
  date: string;
  atl: number;
  ctl: number;
  tsb: number;
  state: StatusKind;
  color?: string;
}

export interface WeeklyLoad {
  week: string;
  mileage: number;
  calories: number;
  steps: number;
  state: StatusKind;
}
