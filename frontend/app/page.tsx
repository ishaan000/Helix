"use client";

import { Box } from "@mui/material";
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
        overflow: "hidden", // prevent scrollbars from wrapping
      }}
    >
      {/* Left Panel (Chat) */}
      <Box
        sx={{ width: "35%", borderRight: "1px solid #eee", overflow: "hidden" }}
      >
        <Chat messages={messages} sendMessage={sendMessage} status={status} />
      </Box>

      {/* Right Panel (Workspace) */}
      <Box sx={{ width: "65%", overflow: "hidden" }}>
        <Workspace sequence={sequence} />
      </Box>
    </Box>
  );
}
