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
  source?: string;
  snippet: string;
  link?: string;
}

const EXAMPLE_PROMPTS = [
  "Generate a sequence for a Founding Engineer in SF",
  "Search for a UX Designer in SF proficient in Figma",
  "Write an offer letter for the UX lead at SellScale.",
  "Generate a casual outreach for a Backend Engineer in Chicago",
  "Search for a Software Engineer in Austin that knows React and Node",
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
          {result.snippet && (
            <Typography variant="body2" sx={{ mt: 1, color: "text.secondary" }}>
              {result.snippet}
            </Typography>
          )}
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

    const getStatusMessage = () => {
      if (status.step) {
        // Check for tool usage in the step message
        if (status.step.includes("searching")) {
          return "🔍 Searching for relevant profiles and information...";
        } else if (status.step.includes("analyzing")) {
          return "📊 Analyzing the search results and crafting a response...";
        } else if (status.step.includes("generating")) {
          return "✨ Generating personalized content based on the findings...";
        }
        return status.step;
      }
      return "Processing your request";
    };

    return (
      <Box sx={{ my: 2 }}>
        <Typography
          variant="body2"
          sx={{
            fontStyle: "italic",
            display: "flex",
            alignItems: "center",
            gap: 1,
            color: getStatusColor(),
            transition: "all 0.3s ease",
            mb: 1,
          }}
        >
          <span>{getStatusEmoji()}</span>
          <span>{getStatusMessage()}</span>
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
        {status.step && (
          <Typography
            variant="caption"
            sx={{
              color: "text.secondary",
              display: "block",
              ml: 4,
            }}
          >
            This may take a few moments while I gather the best information for
            you
          </Typography>
        )}
      </Box>
    );
  };

  const parseSearchResults = (content: string): SearchResult[] | null => {
    // Check if the content contains search results
    if (!content.includes("professionals matching your search")) return null;

    const results: SearchResult[] = [];
    const lines = content.split("\n");
    let currentResult: Partial<SearchResult> = {};

    // Find the start of search results
    let startIndex = 0;
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes("professionals matching your search")) {
        startIndex = i;
        break;
      }
    }

    // Process only the search results section
    for (let i = startIndex; i < lines.length; i++) {
      const line = lines[i];

      // Find where suggestions start
      if (
        line.includes("Generate a personalized outreach") ||
        line.includes("Get more details about") ||
        line.includes("Refine the search")
      ) {
        break;
      }

      // Skip only the initial count line
      if (line.includes("professionals matching your search")) {
        continue;
      }

      // Handle numbered entries
      if (line.match(/^\d+\./)) {
        if (Object.keys(currentResult).length > 0) {
          results.push(currentResult as SearchResult);
        }
        currentResult = { name: line.replace(/^\d+\.\s*/, "") };
      }
      // Handle source lines
      else if (line.startsWith("   Source:")) {
        currentResult.source = line.replace("   Source:", "").trim();
      }
      // Handle current/description lines
      else if (line.startsWith("   Current:") || line.startsWith("   ")) {
        const cleanLine = line.replace(/^(   Current:|   )/, "").trim();
        if (cleanLine) {
          currentResult.snippet = cleanLine;
        }
      }
      // Handle profile links
      else if (line.startsWith("Profile:")) {
        currentResult.link = line.replace("Profile:", "").trim();
      }
    }

    // Add the last result if it exists
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
          <Fade
            key={i}
            in
            timeout={500}
            style={{
              transformOrigin: msg.sender === "ai" ? "0 0" : "100% 0",
              transition: "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
            }}
          >
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                gap: 1,
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                maxWidth: "80%",
                animation:
                  msg.sender === "ai"
                    ? "messageAppear 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
                    : "none",
                "@keyframes messageAppear": {
                  "0%": {
                    opacity: 0,
                    transform: "translateY(10px) scale(0.98)",
                  },
                  "100%": {
                    opacity: 1,
                    transform: "translateY(0) scale(1)",
                  },
                },
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: "text.secondary",
                  alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                  opacity: 0,
                  animation: "fadeIn 0.3s ease forwards",
                  "@keyframes fadeIn": {
                    "0%": { opacity: 0 },
                    "100%": { opacity: 1 },
                  },
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
                  boxShadow:
                    msg.sender === "ai"
                      ? "0 4px 20px rgba(151, 71, 255, 0.1)"
                      : "none",
                  transition: "all 0.3s ease",
                  "&:hover": {
                    boxShadow:
                      msg.sender === "ai"
                        ? "0 6px 24px rgba(151, 71, 255, 0.15)"
                        : "none",
                  },
                }}
              >
                {msg.sender === "ai" && parseSearchResults(msg.content) ? (
                  <>
                    <Typography
                      variant="body1"
                      sx={{
                        color: "text.primary",
                        whiteSpace: "pre-line",
                        mb: 2,
                      }}
                    >
                      {msg.content.split("\n\n")[0]}
                    </Typography>
                    <SearchResultsBox
                      results={parseSearchResults(msg.content)!}
                    />
                    <Box
                      sx={{
                        mt: 2,
                        p: 2,
                        background: "rgba(151, 71, 255, 0.05)",
                        borderRadius: "12px",
                      }}
                    >
                      <Typography
                        variant="body1"
                        sx={{
                          color: "text.primary",
                          whiteSpace: "pre-line",
                        }}
                      >
                        {msg.content.split("Would you like to:")[1]}
                      </Typography>
                    </Box>
                  </>
                ) : (
                  <Typography
                    variant="body1"
                    sx={{
                      color: msg.sender === "user" ? "white" : "text.primary",
                      whiteSpace: "pre-line",
                    }}
                  >
                    {msg.content}
                  </Typography>
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
