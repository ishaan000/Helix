import { useState, useEffect } from "react";
import { sendChatMessage } from "../utils/api";
import io from "socket.io-client";

const socket = io(process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001");

export interface ChatMessage {
  sender: "user" | "ai";
  content: string;
  timestamp?: string;
}

export interface SequenceStep {
  step_number: number;
  content: string;
}

export type LoadingStatus = {
  state: "thinking" | "generating" | "processing" | null;
  step?: string;
};

export const useChat = (sessionId: string | null) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sequence, setSequence] = useState<SequenceStep[]>([]);
  const [status, setStatus] = useState<LoadingStatus>({ state: null });
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(
    sessionId
  );

  // Update currentSessionId when sessionId prop changes
  useEffect(() => {
    setCurrentSessionId(sessionId);
  }, [sessionId]);

  // Create a new session if needed
  const createSession = async () => {
    try {
      const user_id = localStorage.getItem("user_id");
      if (!user_id) throw new Error("No user_id found");

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

      if (!res.ok) {
        const error = await res.text();
        throw new Error(`Failed to create session: ${error}`);
      }

      const data = await res.json();
      setCurrentSessionId(data.session_id);
      return data.session_id;
    } catch (error) {
      console.error("Error creating session:", error);
      throw error;
    }
  };

  // 🔄 Fetch existing messages and sequence on session change
  useEffect(() => {
    if (!currentSessionId) return;

    const fetchData = async () => {
      try {
        // Fetch messages
        const messagesRes = await fetch(
          `${
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"
          }/sessions/${currentSessionId}/messages`
        );
        if (!messagesRes.ok) throw new Error("Failed to fetch messages");
        const messagesData = await messagesRes.json();
        setMessages(messagesData);

        // Fetch sequence
        const sequenceRes = await fetch(
          `${
            process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001"
          }/sequence/${currentSessionId}`
        );
        if (sequenceRes.ok) {
          const sequenceData = await sequenceRes.json();
          setSequence(sequenceData);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [currentSessionId]);

  // 🔔 WebSocket listener for sequence updates
  useEffect(() => {
    if (!currentSessionId) return;

    const handleSequenceUpdate = (data: {
      session_id: string;
      sequence: SequenceStep[];
    }) => {
      if (data.session_id === currentSessionId) {
        console.log("🔁 Real-time update received", data);
        setSequence(data.sequence);
      }
    };

    socket.on("sequence_updated", handleSequenceUpdate);
    return () => {
      socket.off("sequence_updated", handleSequenceUpdate);
    };
  }, [currentSessionId]);

  const sendMessage = async (content: string) => {
    try {
      // Create a new session if none exists
      const sessionIdToUse = currentSessionId || (await createSession());
      if (!sessionIdToUse) throw new Error("Failed to create or get session");

      setMessages((prev) => [...prev, { sender: "user", content }]);
      setStatus({ state: "thinking", step: "Analyzing your request" });

      const data = await sendChatMessage(content, sessionIdToUse);

      if (!data.sequence) {
        setMessages((prev) => [
          ...prev,
          { sender: "ai", content: data.response },
        ]);
        setStatus({ state: null });
        return;
      }

      const showGenerationSteps = async () => {
        setStatus({ state: "generating", step: "Identifying key milestones" });
        await new Promise((res) => setTimeout(res, 1000));

        setStatus({ state: "generating", step: "Planning sequence steps" });
        await new Promise((res) => setTimeout(res, 1000));

        setStatus({
          state: "generating",
          step: "Creating detailed instructions",
        });
        await new Promise((res) => setTimeout(res, 1000));

        // Update both sequence and messages in a single state update
        setSequence(data.sequence);
        setMessages((prev) => {
          // Check if the AI message is already in the state
          const lastMessage = prev[prev.length - 1];
          if (
            lastMessage?.sender === "ai" &&
            lastMessage?.content === data.response
          ) {
            return prev;
          }
          return [...prev, { sender: "ai", content: data.response }];
        });
        setStatus({ state: null });
      };

      await showGenerationSteps();
    } catch (error) {
      console.error("Error sending message:", error);
      setStatus({ state: null });
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          content: "I apologize, but I encountered an error. Please try again.",
        },
      ]);
    }
  };

  return {
    messages,
    sequence,
    status,
    sendMessage,
  };
};
