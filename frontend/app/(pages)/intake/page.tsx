// app/register/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useRegister } from "../../hooks/useIntake";
import {
  Box,
  TextField,
  MenuItem,
  Button,
  Typography,
  CircularProgress,
} from "@mui/material";

const tones = ["professional", "casual", "bold", "friendly", "formal"];

export default function IntakePage() {
  const router = useRouter();
  const { register, loading, error } = useRegister();

  const [form, setForm] = useState({
    name: "",
    email: "",
    company: "",
    title: "",
    industry: "",
    tone: "professional",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async () => {
    const userId = await register(form);
    if (userId) {
      // Optionally: save userId to localStorage or context here
      router.push("/chat"); // or wherever your main chat page lives
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", mt: 8, px: 2 }}>
      <Typography variant="h4" gutterBottom>
        Register to Use Helix
      </Typography>

      <Box
        component="form"
        sx={{ display: "flex", flexDirection: "column", gap: 2 }}
      >
        <TextField
          label="Name"
          name="name"
          value={form.name}
          onChange={handleChange}
          required
        />
        <TextField
          label="Email"
          name="email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <TextField
          label="Company"
          name="company"
          value={form.company}
          onChange={handleChange}
          required
        />
        <TextField
          label="Title"
          name="title"
          value={form.title}
          onChange={handleChange}
        />
        <TextField
          label="Industry"
          name="industry"
          value={form.industry}
          onChange={handleChange}
        />
        <TextField
          select
          label="Preferred Tone"
          name="tone"
          value={form.tone}
          onChange={handleChange}
        >
          {tones.map((tone) => (
            <MenuItem key={tone} value={tone}>
              {tone.charAt(0).toUpperCase() + tone.slice(1)}
            </MenuItem>
          ))}
        </TextField>

        <Button
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : "Continue"}
        </Button>

        {error && (
          <Typography color="error" variant="body2">
            {error}
          </Typography>
        )}
      </Box>
    </Box>
  );
}
