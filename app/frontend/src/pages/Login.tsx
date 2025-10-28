import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  Paper,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { authService } from '../services/auth.service';
import { useAuthStore } from '../store/authStore';

const loginSchema = yup.object({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().required('Password is required'),
}).required();

type LoginFormData = yup.InferType<typeof loginSchema>;

const LoginPage = () => {
  const navigate = useNavigate();
  const { setUser, setToken } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: yupResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      const response = await authService.login(data);
      setToken(response.token);
      setUser(response.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Login
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
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

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Logging in...' : 'Login'}
            </Button>

            <Button
              fullWidth
              variant="text"
              onClick={() => navigate('/register')}
            >
              Don't have an account? Register
            </Button>
          </form>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;