"use client";
import React from "react";
import { Box } from "@mui/material";
import { keyframes } from "@emotion/react";

// Animation keyframes
const gradientAnimation = keyframes`
  0% {
    background-position: 0% 50%;
  }
  25% {
    background-position: 50% 100%;
  }
  50% {
    background-position: 100% 50%;
  }
  75% {
    background-position: 50% 0%;
  }
  100% {
    background-position: 0% 50%;
  }
`;

// Create a subtle pulse animation
const pulseAnimation = keyframes`
  0% {
    opacity: 0.7;
  }
  50% {
    opacity: 0.9;
  }
  100% {
    opacity: 0.7;
  }
`;

interface GradientBackgroundProps {
  children?: React.ReactNode;
  centerContent?: boolean;
  allowScroll?: boolean;
}

export default function GradientBackground({ 
  children, 
  centerContent = true,
  allowScroll = false
}: GradientBackgroundProps) {
  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: allowScroll ? "auto" : "hidden",
        display: centerContent ? "flex" : "block",
        flexDirection: "column",
        alignItems: centerContent ? "center" : "flex-start",
        justifyContent: centerContent ? "center" : "flex-start",
      }}
    >
      {/* Dynamic background layer */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: -1,
          background:
            "linear-gradient(-45deg, #0f0018, #150020, #12001c, #08000e)",
          backgroundSize: "400% 400%",
          animation: `${gradientAnimation} 15s ease infinite`,
        }}
      />

      {/* Additional moving elements */}
      <Box
        sx={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: -1,
          opacity: 0.2,
          background:
            "radial-gradient(circle at 20% 30%, rgba(120, 40, 200, 0.35) 0%, transparent 30%), " +
            "radial-gradient(circle at 80% 70%, rgba(70, 10, 120, 0.35) 0%, transparent 40%)",
          backgroundSize: "200% 200%",
          animation: `${gradientAnimation} 20s ease-in-out infinite reverse, ${pulseAnimation} 8s ease-in-out infinite`,
        }}
      />

      {/* Content */}
      {children}
    </Box>
  );
}
