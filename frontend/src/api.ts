import axios from 'axios';
import { DealScreenResponse, MemoResponse } from './types';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
});

export const screenDeal = async (payload: object): Promise<DealScreenResponse> => {
  const { data } = await client.post<DealScreenResponse>('/api/screen', payload);
  return data;
};

export const generateMemo = async (screenResult: DealScreenResponse, analystNotes?: string): Promise<MemoResponse> => {
  const { data } = await client.post<MemoResponse>('/api/memo', {
    screen_result: screenResult,
    analyst_notes: analystNotes || null,
  });
  return data;
};

export const fetchHistory = async (): Promise<DealScreenResponse[]> => {
  const { data } = await client.get<DealScreenResponse[]>('/api/history');
  return data;
};
