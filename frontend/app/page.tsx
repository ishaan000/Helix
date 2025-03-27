"use client";

import { Box, Typography } from "@mui/material";
import Chat from "../app/components/Chat";
import Workspace from "../app/components/Workspace";
import { useChat } from "../app/hooks/useChat";

export default function HomePage() {
  const { messages, sequence, sendMessage, status } = useChat();

  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        background: "linear-gradient(145deg, #0A0A0F 0%, #12121F 100%)",
        justifyContent: "center",
      }}
    >
      {/* Main Container */}
      <Box
        sx={{
          width: sequence.length > 0 ? "100%" : "800px",
          height: "100%",
          display: "flex",
          transition: "all 0.5s ease-in-out",
        }}
      >
        {/* Chat Panel */}
        <Box
          sx={{
            width: sequence.length > 0 ? "35%" : "100%",
            height: "100%",
            transition: "all 0.5s ease-in-out",
            borderRight:
              sequence.length > 0
                ? "1px solid rgba(255, 255, 255, 0.1)"
                : "none",
            position: "relative",
          }}
        >
          {messages.length === 0 && (
            <Typography
              variant="h1"
              sx={{
                background: "linear-gradient(145deg, #9747FF 0%, #7B2FFF 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                textAlign: "center",
                fontSize: { xs: "3rem", sm: "4rem", md: "5rem" },
                fontWeight: 700,
                position: "absolute",
                top: "30%",
                left: "50%",
                transform: "translateX(-50%)",
                width: "100%",
                zIndex: 1,
              }}
            >
              Helix
            </Typography>
          )}
          <Chat messages={messages} sendMessage={sendMessage} status={status} />
        </Box>

        {/* Workspace Panel */}
        {sequence.length > 0 && (
          <Box
            sx={{
              width: "65%",
              overflow: "hidden",
            }}
          >
            <Workspace sequence={sequence} />
          </Box>
        )}
      </Box>
    </Box>
  );
}
