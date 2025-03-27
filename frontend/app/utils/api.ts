export const sendChatMessage = async (message: string, sessionId = 1) => {
  const apiUrl = process.env.API_URL || "http://localhost:5001";
  const res = await fetch(`${apiUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok) {
    const errorDetails = await res.text();
    throw new Error(
      `Chat API failed with status ${res.status}: ${errorDetails}`
    );
  }
  const data = await res.json();
  console.log("Raw API Response:", { data, sessionId }); // Debug log
  return data;
};
