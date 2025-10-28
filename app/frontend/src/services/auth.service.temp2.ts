export const authService = {
  async login(data: LoginData): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/auth/login', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiErrorResponse>;
        throw new Error(axiosError.response?.data?.detail || 'Error al iniciar sesión');
      }
      throw error;
    }
  },

  async register(data: RegisterData): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/auth/register', data);
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
  }
};