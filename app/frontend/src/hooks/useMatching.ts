import { useQuery } from '@tanstack/react-query';
import { matchingService } from '../services/matching.service';

export const useMatching = () => {
  const {
    data: popularSkills,
    isLoading: isLoadingPopular,
  } = useQuery({
    queryKey: ['popularSkills'],
    queryFn: () => matchingService.getPopularSkills(),
  });

  const searchStudents = async (params: {
    skills?: string[];
    major?: string;
    year?: number;
    query?: string;
  }) => {
    return matchingService.searchStudents(params);
  };

  const getSuggestedSkills = async (query: string) => {
    return matchingService.getSuggestedSkills(query);
  };

  return {
    popularSkills,
    isLoadingPopular,
    searchStudents,
    getSuggestedSkills,
  };
};