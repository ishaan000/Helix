"use client";

import { Box, Typography, IconButton } from "@mui/material";
import Chat from "../../components/Chat";
import Workspace from "../../components/Workspace";
import ChatSidebar from "../../components/ChatSidebar";
import { useChat } from "../../hooks/useChat";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import ViewStreamIcon from "@mui/icons-material/ViewStream";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session");
  const { messages, sequence, sendMessage, status } = useChat(sessionId);
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  const [isSequenceVisible, setIsSequenceVisible] = useState(true);

  // Check for user authentication
  useEffect(() => {
    const user_id = localStorage.getItem("user_id");
    if (!user_id) {
      console.log("No user_id found, redirecting to intake");
      router.push("/intake");
    }
  }, [router]);

  // Auto-minimize sidebar when workspace opens
  useEffect(() => {
    if (sequence.length > 0) {
      setIsSidebarExpanded(false);
      setIsSequenceVisible(true);
    }
  }, [sequence]);

  return (
    <Box
      sx={{
        display: "flex",
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        background: "linear-gradient(145deg, #0A0A0F 0%, #12121F 100%)",
      }}
    >
      <ChatSidebar
        onSelect={(id) => router.push(`/chat?session=${id}`)}
        isExpanded={isSidebarExpanded}
        onToggleExpand={() => setIsSidebarExpanded(!isSidebarExpanded)}
      />

      <Box
        sx={{
          flex: 1,
          display: "flex",
          width: "100%",
          position: "relative",
        }}
      >
        <Box
          sx={{
            width: sequence.length > 0 && isSequenceVisible ? "35%" : "100%",
            height: "100%",
            transition: "all 0.5s ease-in-out",
            borderRight:
              sequence.length > 0 && isSequenceVisible
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

        {sequence.length > 0 && isSequenceVisible && (
          <Box sx={{ width: "65%", overflow: "hidden" }}>
            <Workspace
              sequence={sequence}
              onMinimize={() => setIsSequenceVisible(false)}
            />
          </Box>
        )}

        {sequence.length > 0 && !isSequenceVisible && (
          <IconButton
            onClick={() => setIsSequenceVisible(true)}
            size="small"
            sx={{
              position: "fixed",
              right: 16,
              bottom: "50%",
              transform: "translateY(50%)",
              color: "#9747FF",
              background: "rgba(151, 71, 255, 0.1)",
              width: 32,
              height: 32,
              zIndex: 10,
              "&:hover": {
                background: "rgba(151, 71, 255, 0.2)",
              },
            }}
          >
            <ViewStreamIcon sx={{ fontSize: 20 }} />
          </IconButton>
        )}
      </Box>
    </Box>
  );
}
