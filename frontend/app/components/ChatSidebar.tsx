"use client";

import { useState, useEffect } from "react";
import {
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  IconButton,
  Typography,
  Button,
  Collapse,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Check as CheckIcon,
  Close as CloseIcon,
} from "@mui/icons-material";
import { useRouter, useSearchParams } from "next/navigation";
import io from "socket.io-client";

const socket = io(process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001");

interface Session {
  session_id: string;
  session_title: string;
  created_at: string;
}

interface ChatSidebarProps {
  onSelect: (id: string) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
}

export default function ChatSidebar({
  onSelect,
  isExpanded,
  onToggleExpand,
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentSessionId = searchParams.get("session");

  const fetchSessions = async () => {
    const user_id = localStorage.getItem("user_id");
    if (!user_id) return;

    try {
      const res = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"
        }/sessions?user_id=${user_id}`
      );
      if (!res.ok) throw new Error("Failed to fetch sessions");
      const data = await res.json();
      setSessions(data);
    } catch (error) {
      console.error("Error fetching sessions:", error);
    }
  };

  useEffect(() => {
    fetchSessions();

    // Listen for session title updates
    const handleSessionUpdate = (data: {
      session_id: string;
      session_title: string;
    }) => {
      console.log("Received session update:", data); // Debug log
      setSessions((prev) =>
        prev.map((session) =>
          session.session_id === data.session_id
            ? { ...session, session_title: data.session_title }
            : session
        )
      );
    };

    socket.on("session_updated", handleSessionUpdate);
    return () => {
      socket.off("session_updated", handleSessionUpdate);
    };
  }, []);

  const handleCreateSession = async () => {
    const user_id = localStorage.getItem("user_id");
    if (!user_id) {
      router.push("/intake");
      return;
    }

    try {
      const res = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"
        }/sessions`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id,
            session_title: "New Chat",
          }),
        }
      );

      if (!res.ok) throw new Error("Failed to create session");
      const data = await res.json();
      setSessions((prev) => [data, ...prev]);
      onSelect(data.session_id);
    } catch (error) {
      console.error("Error creating session:", error);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const res = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"
        }/sessions/${sessionId}`,
        {
          method: "DELETE",
        }
      );

      if (!res.ok) throw new Error("Failed to delete session");

      // Remove the session from state
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));

      // Clear editing state if needed
      if (editingId === sessionId) {
        setEditingId(null);
      }

      // If we're deleting the current session, redirect to a new chat
      if (sessionId === currentSessionId) {
        router.push("/chat");
      }
    } catch (error) {
      console.error("Error deleting session:", error);
    }
  };

  const handleUpdateSession = async (sessionId: string) => {
    try {
      const res = await fetch(
        `${
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"
        }/sessions/${sessionId}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_title: editTitle }),
        }
      );

      if (!res.ok) throw new Error("Failed to update session");

      // Update local state
      setSessions((prev) =>
        prev.map((s) =>
          s.session_id === sessionId ? { ...s, session_title: editTitle } : s
        )
      );

      // Emit update via WebSocket to ensure all clients get the update
      socket.emit("session_updated", {
        session_id: sessionId,
        session_title: editTitle,
      });

      setEditingId(null);
    } catch (error) {
      console.error("Error updating session:", error);
    }
  };

  return (
    <Box
      sx={{
        width: isExpanded ? "300px" : "60px",
        height: "100%",
        borderRight: "1px solid rgba(255, 255, 255, 0.1)",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.3s ease-in-out",
        position: "relative",
      }}
    >
      <Box
        sx={{
          p: 2,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        {isExpanded && <Typography variant="h6">Chat History</Typography>}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <IconButton onClick={onToggleExpand} sx={{ color: "white" }}>
            {isExpanded ? <ChevronLeftIcon /> : <ChevronRightIcon />}
          </IconButton>
          {isExpanded && (
            <Button
              startIcon={<AddIcon />}
              onClick={handleCreateSession}
              sx={{ color: "white" }}
            >
              New Chat
            </Button>
          )}
        </Box>
      </Box>

      <Collapse in={isExpanded}>
        <List
          sx={{ flex: 1, overflow: "auto", maxHeight: "calc(100vh - 64px)" }}
        >
          {sessions.map((session) => (
            <ListItem
              key={session.session_id}
              disablePadding
              sx={{ display: "block" }}
            >
              {editingId === session.session_id ? (
                <Box sx={{ p: 1, display: "flex", gap: 1, width: "100%" }}>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    style={{
                      flex: 1,
                      background: "rgba(255, 255, 255, 0.1)",
                      border: "none",
                      padding: "8px",
                      color: "white",
                      borderRadius: "4px",
                    }}
                  />
                  <IconButton
                    size="small"
                    onClick={() => handleUpdateSession(session.session_id)}
                    sx={{ color: "white" }}
                  >
                    <CheckIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => setEditingId(null)}
                    sx={{ color: "white" }}
                  >
                    <CloseIcon />
                  </IconButton>
                </Box>
              ) : (
                <ListItemButton
                  onClick={() => onSelect(session.session_id)}
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    "&:hover": {
                      backgroundColor: "rgba(255, 255, 255, 0.1)",
                    },
                    backgroundColor:
                      currentSessionId === session.session_id
                        ? "rgba(151, 71, 255, 0.1)"
                        : "transparent",
                  }}
                >
                  <ListItemText
                    primary={session.session_title}
                    sx={{
                      "& .MuiListItemText-primary": {
                        color: "white",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      },
                    }}
                  />
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingId(session.session_id);
                        setEditTitle(session.session_title);
                      }}
                      sx={{ color: "white" }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteSession(session.session_id);
                      }}
                      sx={{ color: "white" }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </ListItemButton>
              )}
            </ListItem>
          ))}
        </List>
      </Collapse>

      {!isExpanded && (
        <Box
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            display: "flex",
            flexDirection: "column",
            gap: 2,
          }}
        >
          <IconButton onClick={handleCreateSession} sx={{ color: "white" }}>
            <AddIcon />
          </IconButton>
        </Box>
      )}
    </Box>
  );
}
