import { Student } from '../types';
import { api } from '../utils/api';

export const studentService = {
  async getProfile(): Promise<Student> {
    const response = await api.get<Student>('/students/profile');
    return response.data;
  },

  async updateProfile(data: Partial<Student>): Promise<Student> {
    const response = await api.put<Student>('/students/profile', data);
    return response.data;
  },

  async uploadResume(file: File): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);
    await api.post('/students/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
};