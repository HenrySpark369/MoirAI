import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Layout from './components/Layout';
import LandingPage from './pages/Landing';
import LoginPage from './pages/Login';
import RegisterPage from './pages/Register';
import DashboardPage from './pages/Dashboard';
import ProfilePage from './pages/Profile';
import AdminPage from './pages/Admin';
import NotFoundPage from './pages/NotFound';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const token = useAuthStore((state) => state.token);
  return token ? <>{children}</> : <Navigate to="/login" />;
};

const AppRoutes = () => {
  const token = useAuthStore((state) => state.token);

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={token ? <Navigate to="/dashboard" /> : <LandingPage />} />
      <Route path="/login" element={token ? <Navigate to="/dashboard" /> : <LoginPage />} />
      <Route path="/register" element={token ? <Navigate to="/dashboard" /> : <RegisterPage />} />
      
      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="admin" element={<AdminPage />} />
      </Route>

      {/* 404 route */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes;