import { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminService } from '../services/admin.service';
import type { User } from '../types';

const AdminPage = () => {
  const queryClient = useQueryClient();
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

  const {
    data: users,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['users'],
    queryFn: () => adminService.getUsers(),
  });

  const { data: stats } = useQuery({
    queryKey: ['adminStats'],
    queryFn: () => adminService.getSystemStats(),
  });

  const updateUser = useMutation({
    mutationFn: (data: { userId: string; role: 'student' | 'company' | 'admin' }) =>
      adminService.updateUser(data.userId, { role: data.role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      handleCloseDialog();
    },
  });

  const deleteUser = useMutation({
    mutationFn: (userId: string) => adminService.deleteUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  const handleOpenEditDialog = (user: User) => {
    setSelectedUser(user);
    setIsEditDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setSelectedUser(null);
    setIsEditDialogOpen(false);
  };

  const handleUpdateUser = (role: 'student' | 'company' | 'admin') => {
    if (selectedUser) {
      updateUser.mutate({ userId: selectedUser.id, role });
    }
  };

  const handleDeleteUser = (userId: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      deleteUser.mutate(userId);
    }
  };

  if (isLoading) {
    return (
      <Container>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">Error loading users</Alert>
      </Container>
    );
  }

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Admin Panel
      </Typography>

      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h5">
                  {stats.totalUsers}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Students
                </Typography>
                <Typography variant="h5">
                  {stats.activeStudents}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Companies
                </Typography>
                <Typography variant="h5">
                  {stats.activeCompanies}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users?.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>
                    <Box
                      display="flex"
                      alignItems="center"
                      gap={1}
                    >
                      {user.isActive ? (
                        <CheckCircleIcon color="success" />
                      ) : (
                        <BlockIcon color="error" />
                      )}
                      {user.isActive ? 'Active' : 'Inactive'}
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      onClick={() => handleOpenEditDialog(user)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      onClick={() => handleDeleteUser(user.id)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={isEditDialogOpen} onClose={handleCloseDialog}>
        <DialogTitle>Edit User Role</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={selectedUser?.role || ''}
              label="Role"
              onChange={(e) => {
                const role = e.target.value as 'student' | 'company' | 'admin';
                handleUpdateUser(role);
              }}
            >
              <MenuItem value="student">Student</MenuItem>
              <MenuItem value="company">Company</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={() => {
              if (selectedUser?.role) {
                handleUpdateUser(selectedUser.role);
              }
            }}
            variant="contained"
            color="primary"
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AdminPage;