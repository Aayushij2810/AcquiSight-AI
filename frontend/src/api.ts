import axios from 'axios';
import {
  AddToPortfolioPayload,
  DealScreenResponse,
  MemoResponse,
  PortfolioAnalytics,
  PortfolioInsights,
  PortfolioOpportunity,
} from './types';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60_000,
});

export const screenDeal = async (payload: object): Promise<DealScreenResponse> => {
  const { data } = await client.post<DealScreenResponse>('/api/screen', payload);
  return data;
};

export const generateMemo = async (
  screenResult: DealScreenResponse,
  analystNotes?: string,
): Promise<MemoResponse> => {
  const { data } = await client.post<MemoResponse>('/api/memo', {
    screen_result: screenResult,
    analyst_notes: analystNotes || null,
  });
  return data;
};

export const fetchPortfolio = async (params?: {
  status?: string;
  industry?: string;
  watchlist?: boolean;
  sort_by?: string;
}): Promise<PortfolioOpportunity[]> => {
  const { data } = await client.get<PortfolioOpportunity[]>('/api/portfolio', { params });
  return data;
};

export const fetchPortfolioAnalytics = async (): Promise<PortfolioAnalytics> => {
  const { data } = await client.get<PortfolioAnalytics>('/api/portfolio/analytics');
  return data;
};

export const addToPortfolio = async (payload: AddToPortfolioPayload): Promise<PortfolioOpportunity> => {
  const { data } = await client.post<PortfolioOpportunity>('/api/portfolio', payload);
  return data;
};

export const updatePortfolioOpportunity = async (
  id: number,
  patch: { status?: string; notes?: string; watchlist?: boolean; ic_decision?: string },
): Promise<PortfolioOpportunity> => {
  const { data } = await client.patch<PortfolioOpportunity>(`/api/portfolio/${id}`, patch);
  return data;
};

export const deletePortfolioOpportunity = async (id: number): Promise<void> => {
  await client.delete(`/api/portfolio/${id}`);
};

export const fetchPortfolioInsights = async (): Promise<PortfolioInsights> => {
  const { data } = await client.post<PortfolioInsights>('/api/portfolio/insights');
  return data;
};

export const exportPortfolioCsv = (): string => `${BASE_URL}/api/portfolio/export/csv`;
