import { User } from '../types';
import { api } from '../utils/api';
import axios, { AxiosError } from 'axios';

interface ApiErrorResponse {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

interface LoginResponse {
  token: string;
  user: User;
  api_key: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface RegisterData extends LoginData {
  name: string;
  role: 'student' | 'company';
}

const authService = {
  async login(data: LoginData): Promise<LoginResponse> {
    try {
      console.log('Starting login...', {
        api_url: api.defaults.baseURL,
        email: data.email
      });

      const response = await api.post<LoginResponse>('/auth/login', data);
      
      console.log('Login successful:', {
        status: response.status,
        data: {
          ...response.data,
          token: '[REDACTED]',
          api_key: '[REDACTED]'
        }
      });

      if (!response.data?.token || !response.data?.user) {
        console.error('Invalid response structure:', response.data);
        throw new Error('Invalid server response format');
      }

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiErrorResponse>;
        console.error('Login error:', {
          status: axiosError.response?.status,
          data: axiosError.response?.data,
          url: axiosError.config?.url
        });
        throw new Error(axiosError.response?.data?.detail || 'Error al iniciar sesión');
      }
      throw error;
    }
  },

  async register(data: RegisterData): Promise<LoginResponse> {
    try {
      console.log('Starting registration...', {
        api_url: api.defaults.baseURL,
        data: { ...data, password: '[REDACTED]' }
      });

      const response = await api.post<LoginResponse>('/auth/register', data);
      
      console.log('Registration successful:', {
        status: response.status,
        data: {
          ...response.data,
          token: '[REDACTED]',
          api_key: '[REDACTED]'
        }
      });

      if (!response.data?.token || !response.data?.user) {
        console.error('Invalid response structure:', response.data);
        throw new Error('Invalid server response format');
      }
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiErrorResponse>;
        console.error('Registration error:', {
          status: axiosError.response?.status,
          data: axiosError.response?.data,
          url: axiosError.config?.url,
          headers: axiosError.config?.headers
        });
        throw new Error(axiosError.response?.data?.detail || 'Error en el registro');
      }
      throw error;
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiErrorResponse>;
        throw new Error(axiosError.response?.data?.detail || 'Error al obtener usuario');
      }
      throw error;
    }
  }
};

export { authService };