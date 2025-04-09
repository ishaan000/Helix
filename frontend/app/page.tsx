"use client";
import React from "react";
import { Box, Typography, Button } from "@mui/material";
import Link from "next/link";
import GradientBackground from "./components/GradientBackground";

export default function Home() {
  return (
    <Box
      sx={{
        height: "100vh",
        width: "100%",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <GradientBackground>
        <Typography
          variant="h1"
          sx={{
            fontWeight: 700,
            marginBottom: 3,
            color: "white",
            textShadow: "0 2px 10px rgba(120, 40, 200, 0.45)",
            position: "relative",
            zIndex: 1,
            textAlign: "center",
          }}
        >
          Welcome to Seeker
        </Typography>

        <Typography
          variant="h5"
          sx={{
            marginBottom: 5,
            color: "rgba(255, 255, 255, 0.8)",
            position: "relative",
            zIndex: 1,
            textAlign: "center",
          }}
        >
          Seeker is a platform that helps you find the right job
        </Typography>

        <Link href="/intake" style={{ textDecoration: "none" }}>
          <Button
            variant="outlined"
            size="large"
            sx={{
              color: "white",
              borderColor: "rgba(120, 40, 200, 0.6)",
              padding: "10px 24px",
              borderRadius: "4px",
              fontSize: "1rem",
              transition: "all 0.2s ease",
              position: "relative",
              zIndex: 1,
              "&:hover": {
                borderColor: "rgba(120, 40, 200, 0.9)",
                backgroundColor: "rgba(120, 40, 200, 0.1)",
              },
            }}
          >
            Get Started
          </Button>
        </Link>
      </GradientBackground>
    </Box>
  );
}
