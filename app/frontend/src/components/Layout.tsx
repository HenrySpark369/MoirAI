import { useState } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Person,
  AdminPanelSettings,
  Logout,
} from '@mui/icons-material';
import { useAuthStore } from '../store/authStore';

const DRAWER_WIDTH = 240;

const Layout = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { logout, user } = useAuthStore();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const drawerContent = (
    <>
      <Toolbar />
      <List>
        <ListItem button onClick={() => navigate('/')}>
          <ListItemIcon>
            <Dashboard />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem button onClick={() => navigate('/profile')}>
          <ListItemIcon>
            <Person />
          </ListItemIcon>
          <ListItemText primary="Profile" />
        </ListItem>
        {user?.role === 'admin' && (
          <ListItem button onClick={() => navigate('/admin')}>
            <ListItemIcon>
              <AdminPanelSettings />
            </ListItemIcon>
            <ListItemText primary="Admin Panel" />
          </ListItem>
        )}
        <ListItem button onClick={handleLogout}>
          <ListItemIcon>
            <Logout />
          </ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItem>
      </List>
    </>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{ zIndex: theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            MoirAI Platform
          </Typography>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawerContent}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;