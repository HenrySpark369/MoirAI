import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studentService } from '../services/student.service';
import type { Student } from '../types';

export const useStudentProfile = () => {
  const queryClient = useQueryClient();

  const {
    data: profile,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['studentProfile'],
    queryFn: () => studentService.getProfile(),
  });

  const updateProfile = useMutation({
    mutationFn: (data: Partial<Student>) => studentService.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studentProfile'] });
    },
  });

  const uploadResume = useMutation({
    mutationFn: (file: File) => studentService.uploadResume(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studentProfile'] });
    },
  });

  return {
    profile,
    isLoading,
    error,
    updateProfile,
    uploadResume,
  };
};