export const sendChatMessage = async (message: string, sessionId = 1) => {
  const res = await fetch("http://localhost:5001/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok) throw new Error("Chat API failed");
  return res.json();
};
