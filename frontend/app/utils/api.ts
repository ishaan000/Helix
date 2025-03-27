export const sendChatMessage = async (message: string, sessionId = 1) => {
  const apiUrl = process.env.API_URL || "http://localhost:5001";
  const res = await fetch(`${apiUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok) throw new Error("Chat API failed");
  return res.json();
};
