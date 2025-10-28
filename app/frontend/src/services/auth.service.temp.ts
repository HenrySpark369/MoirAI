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