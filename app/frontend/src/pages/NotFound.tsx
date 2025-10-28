import { Typography, Box } from '@mui/material';

const NotFoundPage = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Typography variant="h1" color="primary">
        404
      </Typography>
      <Typography variant="h5" color="textSecondary">
        Page not found
      </Typography>
    </Box>
  );
};

export default NotFoundPage;