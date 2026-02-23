import axios from 'axios';
import type { DailyStatus, HeartStatus } from './types';

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
