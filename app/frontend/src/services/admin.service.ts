import type { User } from '../types';
import { api } from '../utils/api';

interface UserUpdateData {
  role?: 'student' | 'company' | 'admin';
  isActive?: boolean;
}

export const adminService = {
  async getUsers(): Promise<User[]> {
    const response = await api.get<User[]>('/admin/users');
    return response.data;
  },

  async updateUser(userId: string, data: UserUpdateData): Promise<User> {
    const response = await api.patch<User>(`/admin/users/${userId}`, data);
    return response.data;
  },

  async deleteUser(userId: string): Promise<void> {
    await api.delete(`/admin/users/${userId}`);
  },

  async getSystemStats() {
    const response = await api.get('/admin/stats');
    return response.data;
  }
};