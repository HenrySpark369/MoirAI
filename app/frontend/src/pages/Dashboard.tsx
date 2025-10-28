import { Container, Typography, Box, Paper, Grid } from '@mui/material';
import { useAuthStore } from '../store/authStore';

const DashboardPage = () => {
  const user = useAuthStore((state) => state.user);

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.name}
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Typography variant="body1">
              {user?.role === 'student' ? (
                'Update your profile and find matching opportunities'
              ) : (
                'Post new opportunities and find matching candidates'
              )}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography variant="body1">
              No recent activity to display
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DashboardPage;