import { useState } from "react";
import { signUpUser } from "../utils/api"; // API helper you already added

interface RegisterFormData {
  name: string;
  email: string;
  company: string;
  title: string;
  industry: string;
  companySize: string;
}

export const useRegister = () => {
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = async (
    formData: RegisterFormData
  ): Promise<number | null> => {
    setLoading(true);
    setError(null);

    try {
      const id = await signUpUser(formData); // makes the POST call to /signup
      setUserId(id);
      localStorage.setItem("user_id", id.toString());
      return id;
    } catch (err: unknown) {
      if (err instanceof Error) {
        console.error("Register error:", err);
        setError(err.message);
      } else {
        setError("Something went wrong during registration.");
      }
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { register, userId, loading, error };
};
