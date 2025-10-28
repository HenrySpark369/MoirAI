import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Add timeout
  timeout: 5000,
  // Add CORS settings
  withCredentials: false,
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => {
    // Log successful responses (excluding sensitive data)
    console.log(`API Response [${response.config.method?.toUpperCase()}] ${response.config.url}:`, {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data ? { ...response.data, token: response.data.token ? '[REDACTED]' : undefined } : null
    });
    return response;
  },
  (error) => {
    if (axios.isAxiosError(error)) {
      // Log detailed error information
      console.error('API Error:', {
        message: error.message,
        endpoint: `${error.config?.method?.toUpperCase()} ${error.config?.url}`,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        headers: {
          request: error.config?.headers,
          response: error.response?.headers
        }
      });

      // Handle specific error cases
      if (!error.response) {
        error.message = 'Network error: Server unreachable';
      } else if (error.response.status === 401) {
        // Clear token on authentication error
        localStorage.removeItem('token');
      }
    }
    return Promise.reject(error);
  }
);
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    // Transform error message for better user experience
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.detail ||
                        error.message ||
                        'An unexpected error occurred';
    return Promise.reject({ 
      ...error, 
      message: errorMessage
    });
  }
);