// theme/theme.ts
import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#9747FF" },
    background: {
      default: "#F5F0FF",
      paper: "#ffffff",
    },
    text: {
      primary: "#333333",
      secondary: "#6E6E6E",
    },
  },
  typography: {
    fontFamily: "Inter, sans-serif",
  },
  shape: {
    borderRadius: 16,
  },
});
