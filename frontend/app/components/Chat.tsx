import {
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Fade,
  Chip,
  Link,
  Divider,
} from "@mui/material";
import { useState } from "react";
import { ChatMessage, LoadingStatus } from "../hooks/useChat";
import SendIcon from "@mui/icons-material/Send";
import SearchIcon from "@mui/icons-material/Search";

interface ChatProps {
  messages: ChatMessage[];
  sendMessage: (content: string) => Promise<void>;
  status: LoadingStatus;
}

interface SearchResult {
  name: string;
  source: string;
  snippet: string;
  link?: string;
}

const EXAMPLE_PROMPTS = [
  "Generate a sequence for a Founding Engineer in SF",
  "Search for a UX Designer in SF",

  "Write an offer letter for the UX lead at SellScale.",
  "Generate a casual outreach for a Backend Engineer in Chicago",
  "Search for a Software Engineer in Austin",
];

const SearchResultsBox = ({ results }: { results: SearchResult[] }) => {
  return (
    <Box
      sx={{
        mt: 2,
        p: 2,
        background: "rgba(151, 71, 255, 0.05)",
        borderRadius: "12px",
        border: "1px solid rgba(151, 71, 255, 0.1)",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
        <SearchIcon sx={{ color: "#9747FF" }} />
        <Typography variant="subtitle2" sx={{ color: "#9747FF" }}>
          Search Results
        </Typography>
      </Box>
      {results.map((result, index) => (
        <Box key={index} sx={{ mb: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
            {result.name}
          </Typography>
          <Typography variant="caption" sx={{ color: "text.secondary" }}>
            Source: {result.source}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {result.snippet}
          </Typography>
          {result.link && (
            <Link
              href={result.link}
              target="_blank"
              rel="noopener noreferrer"
              sx={{
                display: "inline-block",
                mt: 1,
                color: "#9747FF",
                textDecoration: "none",
                "&:hover": {
                  textDecoration: "underline",
                },
              }}
            >
              View Profile →
            </Link>
          )}
          {index < results.length - 1 && (
            <Divider sx={{ my: 2, borderColor: "rgba(151, 71, 255, 0.1)" }} />
          )}
        </Box>
      ))}
    </Box>
  );
};

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

  const handleExampleClick = (prompt: string) => {
    setInput(prompt);
  };

  const renderLoadingState = () => {
    if (!status.state) return null;

    const getStatusColor = () => {
      switch (status.state) {
        case "thinking":
          return "#9747FF";
        case "generating":
          return "#B47FFF";
        case "processing":
          return "#7B2FFF";
        default:
          return "#A0A0A0";
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

  const parseSearchResults = (content: string): SearchResult[] | null => {
    // Check if the content contains search results
    if (!content.includes("professionals matching your search")) return null;

    const results: SearchResult[] = [];
    const lines = content.split("\n");
    let currentResult: Partial<SearchResult> = {};

    for (const line of lines) {
      // Stop parsing if we hit the suggestions section
      if (
        line.includes("Generate a personalized outreach") ||
        line.includes("Get more details about") ||
        line.includes("Refine the search")
      ) {
        break;
      }

      if (line.match(/^\d+\./)) {
        if (Object.keys(currentResult).length > 0) {
          results.push(currentResult as SearchResult);
        }
        currentResult = { name: line.replace(/^\d+\.\s*/, "") };
      } else if (line.startsWith("   Source:")) {
        currentResult.source = line.replace("   Source:", "").trim();
      } else if (line.startsWith("   ")) {
        currentResult.snippet = line.trim();
      } else if (line.startsWith("Profile:")) {
        currentResult.link = line.replace("Profile:", "").trim();
      }
    }

    if (Object.keys(currentResult).length > 0) {
      results.push(currentResult as SearchResult);
    }

    return results;
  };

  return (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          overflowY: "auto",
          p: 4,
          "&::-webkit-scrollbar": {
            width: "8px",
          },
          "&::-webkit-scrollbar-track": {
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: "4px",
          },
          "&::-webkit-scrollbar-thumb": {
            background: "rgba(255, 255, 255, 0.1)",
            borderRadius: "4px",
            "&:hover": {
              background: "rgba(255, 255, 255, 0.15)",
            },
          },
        }}
      >
        {messages.map((msg, i) => (
          <Fade key={i} in timeout={300}>
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                gap: 1,
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                maxWidth: "80%",
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: "text.secondary",
                  alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                }}
              >
                {msg.sender === "user" ? "You" : "Helix"}
              </Typography>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  background:
                    msg.sender === "user"
                      ? "linear-gradient(145deg, #9747FF 0%, #7B2FFF 100%)"
                      : "rgba(255, 255, 255, 0.05)",
                  borderRadius: "12px",
                  border:
                    msg.sender === "user"
                      ? "none"
                      : "1px solid rgba(255, 255, 255, 0.1)",
                }}
              >
                <Typography
                  variant="body1"
                  sx={{
                    color: msg.sender === "user" ? "white" : "text.primary",
                    whiteSpace: "pre-line",
                  }}
                >
                  {msg.content}
                </Typography>
                {msg.sender === "ai" && parseSearchResults(msg.content) && (
                  <SearchResultsBox
                    results={parseSearchResults(msg.content)!}
                  />
                )}
              </Paper>
            </Box>
          </Fade>
        ))}
        {renderLoadingState()}
      </Box>

      <Box
        sx={{
          borderTop: "1px solid rgba(255, 255, 255, 0.1)",
          p: 2,
        }}
      >
        {messages.length === 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography
              variant="caption"
              sx={{ color: "text.secondary", mb: 1, display: "block" }}
            >
              Try these example prompts:
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {EXAMPLE_PROMPTS.map((prompt, index) => (
                <Chip
                  key={index}
                  label={prompt}
                  onClick={() => handleExampleClick(prompt)}
                  sx={{
                    backgroundColor: "rgba(151, 71, 255, 0.1)",
                    color: "#9747FF",
                    "&:hover": {
                      backgroundColor: "rgba(151, 71, 255, 0.2)",
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
        )}
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Ask Helix something..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                backgroundColor: "transparent",
                borderRadius: "12px",
                "& fieldset": {
                  borderColor: "rgba(255, 255, 255, 0.1)",
                },
                "&:hover fieldset": {
                  borderColor: "rgba(255, 255, 255, 0.2)",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#9747FF",
                },
              },
            }}
          />
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={!input.trim()}
            sx={{
              minWidth: "48px",
              width: "48px",
              height: "40px",
              borderRadius: "12px",
              p: 0,
            }}
          >
            <SendIcon sx={{ fontSize: 20 }} />
          </Button>
        </Box>
      </Box>
    </Box>
  );
}
