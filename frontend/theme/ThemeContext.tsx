// theme/ThemeContext.tsx
"use client";

import { ThemeProvider as MuiThemeProvider, CssBaseline } from "@mui/material";
import { theme } from "./theme"; // your SellScale-style theme
import React from "react";

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  );
};
