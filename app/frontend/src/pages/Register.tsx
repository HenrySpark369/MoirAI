import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios, { AxiosError } from 'axios';

interface ApiErrorResponse {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  Paper,
  FormControlLabel,
  Radio,
  RadioGroup,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { authService } from '../services/auth.service';
import { useAuthStore } from '../store/authStore';

const registerSchema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup
    .string()
    .min(8, 'Password must be at least 8 characters')
    .required('Password is required'),
  role: yup.string().oneOf(['student', 'company']).required('Role is required'),
}).required();

type RegisterFormData = yup.InferType<typeof registerSchema>;

const RegisterPage = () => {
  const navigate = useNavigate();
  const { setUser, setToken } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: yupResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setError(null); // Clear any previous errors
    try {
      console.log('Submitting registration form:', { ...data, password: '****' });
      const response = await authService.register({
        email: data.email,
        password: data.password,
        name: data.name,
        role: data.role,
      });
      console.log('Registration response:', response);
      
      if (response?.token && response?.user) {
        setToken(response.token);
        setUser(response.user);
        navigate('/');
      } else {
        console.error('Invalid response structure:', response);
        setError('Invalid response from server');
      }
    } catch (error: unknown) {
      console.error('Registration error:', error);
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiErrorResponse>;
        console.error('API Error Details:', {
          status: axiosError.response?.status,
          data: axiosError.response?.data,
          config: {
            url: axiosError.config?.url,
            method: axiosError.config?.method,
            headers: axiosError.config?.headers,
            data: axiosError.config?.data,
          }
        });
        setError(
          axiosError.response?.data?.detail || 
          axiosError.response?.data?.message || 
          axiosError.message || 
          'Registration failed'
        );
      } else {
        setError('An unexpected error occurred');
      }
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Register
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              {...register('name')}
              margin="normal"
              fullWidth
              label="Name"
              error={!!errors.name}
              helperText={errors.name?.message}
            />

            <TextField
              {...register('email')}
              margin="normal"
              fullWidth
              label="Email"
              type="email"
              error={!!errors.email}
              helperText={errors.email?.message}
            />

            <TextField
              {...register('password')}
              margin="normal"
              fullWidth
              label="Password"
              type="password"
              error={!!errors.password}
              helperText={errors.password?.message}
            />

            <RadioGroup
              {...register('role')}
              sx={{ mt: 2 }}
              defaultValue="student"
            >
              <FormControlLabel
                value="student"
                control={<Radio />}
                label="Student"
              />
              <FormControlLabel
                value="company"
                control={<Radio />}
                label="Company"
              />
            </RadioGroup>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Registering...' : 'Register'}
            </Button>

            <Button
              fullWidth
              variant="text"
              onClick={() => navigate('/login')}
            >
              Already have an account? Login
            </Button>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterPage;