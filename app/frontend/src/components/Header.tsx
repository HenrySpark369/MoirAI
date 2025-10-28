import React from 'react';
import { AppBar, Toolbar, Box, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Logo from '../assets/logo.svg';

const Header: React.FC = () => {
  const navigate = useNavigate();

  return (
    <AppBar position="static" sx={{ backgroundColor: '#631333' }}>
      <Toolbar>
        <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
          <img src={Logo} alt="MoirAI Logo" style={{ height: '40px', marginRight: '10px' }} />
        </Box>
        <Box>
          <Button color="inherit" onClick={() => navigate('/students')}>
            Estudiantes
          </Button>
          <Button color="inherit" onClick={() => navigate('/job-scraping')}>
            Oportunidades
          </Button>
          <Button color="inherit" onClick={() => navigate('/auth')}>
            Login
          </Button>
          <Button color="inherit" onClick={() => navigate('/companies')}>
            Empresas
          </Button>
          <Button color="inherit" onClick={() => navigate('/admin')}>
            Admin
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;