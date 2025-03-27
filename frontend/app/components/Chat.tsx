import { Paper, Typography, Box, TextField, Button } from "@mui/material";
import { useState } from "react";
import { ChatMessage, LoadingStatus } from "../hooks/useChat";

interface ChatProps {
  messages: ChatMessage[];
  sendMessage: (content: string) => Promise<void>;
  status: LoadingStatus;
}

export default function Chat({ messages, sendMessage, status }: ChatProps) {
  const [input, setInput] = useState("");

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const currentMessage = input;
    setInput("");

    try {
      await sendMessage(currentMessage);
    } catch (e) {
      console.error("Send failed", e);
    }
  };

  const renderLoadingState = () => {
    if (!status.state) return null;

    const getStatusColor = () => {
      switch (status.state) {
        case "thinking":
          return "info.main";
        case "generating":
          return "success.main";
        case "processing":
          return "secondary.main";
        default:
          return "text.secondary";
      }
    };

    const getStatusEmoji = () => {
      switch (status.state) {
        case "thinking":
          return "🤔";
        case "generating":
          return "✍️";
        case "processing":
          return "⚙️";
        default:
          return "🧠";
      }
    };

    return (
      <Typography
        variant="body2"
        sx={{
          fontStyle: "italic",
          my: 2,
          display: "flex",
          alignItems: "center",
          gap: 1,
          color: getStatusColor(),
          transition: "all 0.3s ease",
        }}
      >
        <span>{getStatusEmoji()}</span>
        <span>{status.step || "Processing"}</span>
        <Box
          component="span"
          sx={{
            display: "inline-block",
            ml: 1,
            animation: "pulse 1.5s infinite",
          }}
        >
          <span className="dot">.</span>
          <span className="dot">.</span>
          <span className="dot">.</span>
        </Box>
      </Typography>
    );
  };

  return (
    <Paper
      elevation={3}
      square
      sx={{ p: 2, height: "100%", overflowY: "auto" }}
    >
      <Typography variant="h6" gutterBottom>
        🧠 Chat with Helix
      </Typography>

      <Box
        sx={{ height: "80%", overflowY: "auto", mb: 2, whiteSpace: "pre-line" }}
      >
        {messages.map((msg, i) => (
          <Typography
            key={i}
            variant="body2"
            color={msg.sender === "user" ? "primary" : "secondary"}
            sx={{ my: 2 }}
          >
            <strong>{msg.sender === "user" ? "You" : "Helix"}:</strong>
            <br />
            {msg.content}
          </Typography>
        ))}

        {renderLoadingState()}
      </Box>

      <Box sx={{ display: "flex" }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Ask Helix something..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault(); // prevent newline
              handleSubmit();
            }
          }}
        />
        <Button variant="contained" onClick={handleSubmit}>
          Send
        </Button>
      </Box>
    </Paper>
  );
}
