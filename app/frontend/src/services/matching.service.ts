import type { Student } from '../types';
import { api } from '../utils/api';

interface SearchParams {
  skills?: string[];
  major?: string;
  year?: number;
  query?: string;
}

interface MatchResponse {
  students: Student[];
  totalMatches: number;
  matchScores: Record<string, number>;
}

export const matchingService = {
  async searchStudents(params: SearchParams): Promise<MatchResponse> {
    const response = await api.get<MatchResponse>('/matching/search', {
      params,
    });
    return response.data;
  },

  async getSuggestedSkills(query: string): Promise<string[]> {
    const response = await api.get<string[]>('/matching/skills/suggest', {
      params: { query },
    });
    return response.data;
  },

  async getPopularSkills(): Promise<string[]> {
    const response = await api.get<string[]>('/matching/skills/popular');
    return response.data;
  }
};