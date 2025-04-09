export const sendChatMessage = async (message: string, sessionId: string) => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";
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

export const signUpUser = async (formData: {
  name: string;
  email: string;
  current_company?: string;
  title: string;
  industry: string;
  preferences: {
    jobTypes: string[];
    targetCompanies: string[];
    targetLocations: string[];
    yearsExperience: number;
    skills: string[];
    jobLevel: string;
  };
}) => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

  const res = await fetch(`${apiUrl}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Signup failed: ${res.status} - ${err}`);
  }

  const data = await res.json();
  return data.user_id;
};
