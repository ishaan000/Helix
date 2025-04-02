import React from "react";
import { Box, Typography } from "@mui/material";
import Link from "next/link";

export default function Home() {
  return (
    <Box
      padding={10}
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="top"
      height="100vh"
    >
      <Typography padding={2} variant="h1">
        Welcome to Helix
      </Typography>
      <Typography variant="body1">
        Helix is a platform that helps you find the right job
      </Typography>
      <Link style={{ marginTop: 20 }} href="/intake">
        Get Started
      </Link>
    </Box>
  );
}
