import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createTheme, ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes";
import "./App.css";

const queryClient = new QueryClient();

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;