// theme/theme.ts
import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#9747FF",
      light: "#B47FFF",
      dark: "#7B2FFF",
    },
    background: {
      default: "#0A0A0F",
      paper: "#12121F",
    },
    text: {
      primary: "#FFFFFF",
      secondary: "#A0A0A0",
    },
  },
  typography: {
    fontFamily: "Inter, sans-serif",
    h1: {
      fontWeight: 700,
      fontSize: "2.5rem",
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "linear-gradient(145deg, #12121F 0%, #1A1A2F 100%)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          borderRadius: 8,
          padding: "8px 16px",
          fontWeight: 600,
        },
        contained: {
          background: "linear-gradient(145deg, #9747FF 0%, #7B2FFF 100%)",
          "&:hover": {
            background: "linear-gradient(145deg, #B47FFF 0%, #9747FF 100%)",
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 8,
            "& fieldset": {
              borderColor: "rgba(255, 255, 255, 0.1)",
            },
            "&:hover fieldset": {
              borderColor: "rgba(255, 255, 255, 0.2)",
            },
            "&.Mui-focused fieldset": {
              borderColor: "#9747FF",
            },
          },
        },
      },
    },
  },
});
