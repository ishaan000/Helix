import { useState } from "react";
import { sendChatMessage } from "../utils/api";

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

  const sendMessage = async (content: string) => {
    setMessages((prev) => [...prev, { sender: "user", content }]);

    try {
      // Initial thinking state
      setStatus({ state: "thinking", step: "Analyzing your request" });

      const data = await sendChatMessage(content);

      if (!data.sequence) {
        setMessages((prev) => [
          ...prev,
          { sender: "ai", content: data.response },
        ]);
        setStatus({ state: null });
      }

      if (data.sequence) {
        // Show sequence generation states with appropriate timing
        const showGenerationSteps = async () => {
          setStatus({
            state: "generating",
            step: "Identifying key milestones",
          });
          await new Promise((resolve) => setTimeout(resolve, 1000));

          setStatus({
            state: "generating",
            step: "Planning sequence steps",
          });
          await new Promise((resolve) => setTimeout(resolve, 1000));

          setStatus({
            state: "generating",
            step: "Creating detailed instructions",
          });
          await new Promise((resolve) => setTimeout(resolve, 1000));

          setSequence(data.sequence);

          setStatus({ state: "processing", step: "Finalizing sequence" });
          await new Promise((resolve) => setTimeout(resolve, 800));

          setStatus({ state: null });
        };

        showGenerationSteps();
      }
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
