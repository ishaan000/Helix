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

const companySizes = ["startup", "small", "medium", "large", "enterprise"];

export default function IntakePage() {
  const router = useRouter();
  const { register, loading, error } = useRegister();

  const [form, setForm] = useState({
    name: "",
    email: "",
    company: "",
    title: "",
    industry: "",
    companySize: "startup",
  });

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    const userId = await register(form);
    if (userId) {
      router.push("/chat");
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
          label="Company Size"
          name="companySize"
          value={form.companySize}
          onChange={handleChange}
        >
          {companySizes.map((size) => (
            <MenuItem key={size} value={size}>
              {size.charAt(0).toUpperCase() + size.slice(1)}
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
