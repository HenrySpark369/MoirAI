import { Box, Button, Container, Grid, Typography } from '@mui/material';
import { Link } from 'react-router-dom';
import { styled } from '@mui/system';

const HeroButton = styled(Button)(() => ({
  borderRadius: '50px',
  padding: '10px 30px',
  fontSize: '1.2rem',
  textTransform: 'none',
}));

const LandingPage = () => {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        backgroundColor: '#FFFFFF', // Solid white background
        color: '#333333',
        display: 'flex',
        flexDirection: 'column',
        width: '100vw',
        overflowX: 'hidden',
      }}
    >
      {/* Header/Navigation */}
      <Box
        sx={{
          py: 2,
          px: 4,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#631333', // Deep red for header
          color: 'white',
          boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
        }}
      >
        <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
          MoirAI
        </Typography>
        <Box>
          <HeroButton
            component={Link}
            to="/login"
            variant="outlined"
            sx={{
              borderColor: 'white',
              color: 'white',
              mr: 2,
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
              },
            }}
          >
            Iniciar Sesión
          </HeroButton>
          <HeroButton
            component={Link}
            to="/register"
            variant="contained"
            sx={{
              backgroundColor: 'white',
              color: '#631333',
              '&:hover': {
                backgroundColor: '#F5F5F5',
              },
            }}
          >
            Registrarse
          </HeroButton>
        </Box>
      </Box>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ mt: 8, mb: 12, textAlign: 'center' }}>
        <Typography
          variant="h2"
          component="h2"
          sx={{
            fontWeight: 700,
            mb: 4,
            fontSize: { xs: '2.5rem', md: '3.5rem' },
            lineHeight: 1.2,
            color: '#333333', // Dark gray text color
          }}
        >
          Conectamos Talento Universitario con Oportunidades Laborales
        </Typography>
        <Typography variant="h5" sx={{ mb: 4, opacity: 0.9, color: '#555555' }}>
          Plataforma de matching laboral impulsada por IA para estudiantes de la UNRC
        </Typography>
        <HeroButton
          component={Link}
          to="/register"
          variant="contained"
          sx={{
            backgroundColor: '#631333',
            color: 'white',
            '&:hover': {
              backgroundColor: '#7A1A3D',
            },
            mr: 2,
          }}
        >
          Comienza Ahora
        </HeroButton>
        <HeroButton
          component={Link}
          to="/about"
          variant="outlined"
          sx={{
            borderColor: '#631333',
            color: '#631333',
            '&:hover': {
              backgroundColor: 'rgba(99, 19, 51, 0.1)',
            },
          }}
        >
          Conoce Más
        </HeroButton>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Box
              sx={{
                textAlign: 'center',
                p: 3,
                background: '#F5F5F5', // Light gray background
                borderRadius: '10px',
                boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
              }}
            >
              <Typography variant="h4" sx={{ mb: 2, color: '#333333' }}>
                IA Avanzada
              </Typography>
              <Typography sx={{ color: '#555555' }}>
                Algoritmos de matching inteligente que analizan habilidades técnicas y blandas
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box
              sx={{
                textAlign: 'center',
                p: 3,
                background: '#F5F5F5',
                borderRadius: '10px',
                boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
              }}
            >
              <Typography variant="h4" sx={{ mb: 2, color: '#333333' }}>
                Perfil Dinámico
              </Typography>
              <Typography sx={{ color: '#555555' }}>
                Showcase tus proyectos y habilidades de forma interactiva
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box
              sx={{
                textAlign: 'center',
                p: 3,
                background: '#F5F5F5',
                borderRadius: '10px',
                boxShadow: '0px 4px 6px rgba(0, 0, 0, 0.1)',
              }}
            >
              <Typography variant="h4" sx={{ mb: 2, color: '#333333' }}>
                Conexión Directa
              </Typography>
              <Typography sx={{ color: '#555555' }}>
                Vinculación inmediata con empresas que buscan tu talento
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* Call to Action */}
      <Container maxWidth="md" sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="h3" sx={{ mb: 4, color: '#333333' }}>
          ¿Listo para dar el siguiente paso?
        </Typography>
        <HeroButton
          component={Link}
          to="/register"
          variant="contained"
          sx={{
            backgroundColor: '#631333',
            color: 'white',
            '&:hover': {
              backgroundColor: '#7A1A3D',
            },
          }}
        >
          Crea tu Cuenta Gratis
        </HeroButton>
      </Container>

      {/* Footer */}
      <Box sx={{ bgcolor: '#631333', py: 4, mt: 8, color: 'white' }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                MoirAI
              </Typography>
              <Typography variant="body2">
                Una iniciativa de la Universidad Nacional de Río Cuarto
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Contacto
              </Typography>
              <Typography variant="body2">
                Email: contacto@moirai.unrc.edu.ar
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Enlaces
              </Typography>
              <Box sx={{ '& > *': { mr: 2 } }}>
                <Link to="/about" style={{ color: 'white' }}>
                  Sobre Nosotros
                </Link>
                <Link to="/privacy" style={{ color: 'white' }}>
                  Privacidad
                </Link>
                <Link to="/terms" style={{ color: 'white' }}>
                  Términos
                </Link>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;