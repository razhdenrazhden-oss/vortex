import axios from 'axios';
import type { ActivityItem, DailyStatus, HeartStatus, LoadPoint } from './types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
});

export async function fetchDailyStatus(userId: number): Promise<DailyStatus[]> {
  const { data } = await api.get<DailyStatus[]>('/daily-status', { params: { user_id: userId } });
  return data;
}

export async function fetchHeartStatus(userId: number): Promise<HeartStatus> {
  const { data } = await api.get<HeartStatus>(`/users/${userId}/heart-status`);
  return data;
}

export async function fetchUserActivities(startDate?: string, endDate?: string): Promise<ActivityItem[]> {
  const { data } = await api.get<ActivityItem[]>('/user/activities', { params: { start_date: startDate, end_date: endDate } });
  return data;
}

export async function fetchUserForm(): Promise<LoadPoint[]> {
  const { data } = await api.get<{ points: Array<{ date: string; atl: number; ctl: number; tsb: number; load_state: string; load_color: string }> }>('/user/form');
  return data.points.map((p) => ({
    date: p.date,
    atl: p.atl,
    ctl: p.ctl,
    tsb: p.tsb,
    state: p.load_state as LoadPoint['state'],
    color: p.load_color
  }));
}

export async function postManualBiometrics(input: {
  user_id: number;
  entry_date: string;
  hr?: number;
  hrv?: number;
  lactate?: number;
  power?: number;
}) {
  await api.post('/biometrics', input);
}
