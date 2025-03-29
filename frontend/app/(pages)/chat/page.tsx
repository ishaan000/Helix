"use client";

import { Box, Typography } from "@mui/material";
import Chat from "../../components/Chat";
import Workspace from "../../components/Workspace";
import ChatSidebar from "../../components/ChatSidebar";
import { useChat } from "../../hooks/useChat";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session");
  const { messages, sequence, sendMessage, status } = useChat(sessionId);
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);

  // Debug log for sequence state
  useEffect(() => {
    console.log("Sequence state:", sequence);
  }, [sequence]);

  // Check for user authentication
  useEffect(() => {
    const user_id = localStorage.getItem("user_id");
    if (!user_id) {
      console.log("No user_id found, redirecting to intake");
      router.push("/intake");
    }
  }, [router]);

  // Auto-minimize sidebar when sequence is available
  useEffect(() => {
    if (sequence && sequence.length > 0) {
      setIsSidebarExpanded(false);
    }
  }, [sequence]);

  const hasValidSequence =
    sequence && sequence.length > 0 && sequence.some((step) => step.content);

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
            width: hasValidSequence ? "35%" : "100%",
            height: "100%",
            transition: "all 0.5s ease-in-out",
            borderRight: hasValidSequence
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

        {hasValidSequence && (
          <Box sx={{ width: "65%", overflow: "hidden" }}>
            <Workspace sequence={sequence} />
          </Box>
        )}
      </Box>
    </Box>
  );
}
