import { useState } from "react";
import { sendChatMessage } from "../utils/api";
import { useEffect } from "react";
import io from "socket.io-client";

const socket = io(process.env.REACT_APP_SOCKET_URL || "http://localhost:5001");
export interface ChatMessage {
  sender: "user" | "ai";
  content: string;
}

export interface SequenceStep {
  step_number: number;
  content: string;
}

export type LoadingStatus = {
  state: "thinking" | "generating" | "processing" | null;
  step?: string;
};

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sequence, setSequence] = useState<SequenceStep[]>([]);
  const [status, setStatus] = useState<LoadingStatus>({ state: null });
  const [sessionId] = useState(1); // keep it simple for now

  useEffect(() => {
    const handleSequenceUpdate = (data: {
      session_id: number;
      sequence: SequenceStep[];
    }) => {
      if (data.session_id === sessionId) {
        console.log("🔁 Real-time update received", data);
        setSequence(data.sequence);
      }
    };

    socket.on("sequence_updated", handleSequenceUpdate);

    return () => {
      socket.off("sequence_updated", handleSequenceUpdate);
    };
  }, [sessionId]);

  const sendMessage = async (content: string) => {
    setMessages((prev) => [...prev, { sender: "user", content }]);

    try {
      setStatus({ state: "thinking", step: "Analyzing your request" });

      const data = await sendChatMessage(content, sessionId);

      // ✅ Case 1: No sequence, just a regular reply
      if (!data.sequence) {
        setMessages((prev) => [
          ...prev,
          { sender: "ai", content: data.response },
        ]);
        setStatus({ state: null });
        return;
      }

      // ✅ Case 2: Sequence was generated
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

        setSequence(data.sequence);

        setStatus({ state: "processing", step: "Finalizing sequence" });
        await new Promise((res) => setTimeout(res, 800));

        setStatus({ state: null });

        // ✅ Only now, after the sequence shows, drop follow-up message
        setMessages((prev) => [
          ...prev,
          { sender: "ai", content: data.response },
        ]);
      };

      await showGenerationSteps();
    } catch (e) {
      console.error("Error in sendMessage:", e);
      setMessages((prev) => [
        ...prev,
        { sender: "ai", content: "Sorry, something went wrong!" },
      ]);
      setStatus({ state: null });
    }
  };

  return { messages, sequence, sendMessage, status };
};
