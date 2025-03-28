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
  Paper,
  InputAdornment,
} from "@mui/material";
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Business as BusinessIcon,
  Work as WorkIcon,
  Category as CategoryIcon,
  Groups as GroupsIcon,
} from "@mui/icons-material";

const companySizes = [
  { value: "startup", label: "Startup (1-10 employees)" },
  { value: "small", label: "Small (11-50 employees)" },
  { value: "medium", label: "Medium (51-200 employees)" },
  { value: "large", label: "Large (201-1000 employees)" },
  { value: "enterprise", label: "Enterprise (1000+ employees)" },
];

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
      <Typography
        variant="h4"
        gutterBottom
        sx={{
          animation: "titleAppear 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
          "@keyframes titleAppear": {
            "0%": {
              opacity: 0,
              transform: "translateY(-10px)",
            },
            "100%": {
              opacity: 1,
              transform: "translateY(0)",
            },
          },
        }}
      >
        Let Helix Get to Know You
      </Typography>
      <Typography
        variant="subtitle1"
        color="text.secondary"
        sx={{
          mb: 4,
          animation: "fadeIn 0.5s ease forwards",
          "@keyframes fadeIn": {
            "0%": { opacity: 0 },
            "100%": { opacity: 1 },
          },
        }}
      >
        I&apos;m Helix, and I&apos;d love to understand your needs better. Share
        a bit about yourself so I can provide you with the most relevant and
        personalized experience.
      </Typography>

      <Paper
        elevation={0}
        sx={{
          p: 4,
          borderRadius: 2,
          bgcolor: "background.paper",
          animation: "formAppear 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
          "@keyframes formAppear": {
            "0%": {
              opacity: 0,
              transform: "translateY(20px) scale(0.98)",
            },
            "100%": {
              opacity: 1,
              transform: "translateY(0) scale(1)",
            },
          },
          boxShadow: "0 4px 20px rgba(151, 71, 255, 0.1)",
          transition: "all 0.3s ease",
          "&:hover": {
            boxShadow: "0 6px 24px rgba(151, 71, 255, 0.15)",
          },
        }}
      >
        <Box
          component="form"
          sx={{ display: "flex", flexDirection: "column", gap: 3 }}
        >
          <TextField
            label="Name"
            name="name"
            value={form.name}
            onChange={handleChange}
            required
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <PersonIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                transition: "all 0.3s ease",
                "&:hover": {
                  "& fieldset": {
                    borderColor: "rgba(151, 71, 255, 0.5)",
                  },
                },
                "&.Mui-focused": {
                  "& fieldset": {
                    borderColor: "#9747FF",
                    boxShadow: "0 0 0 2px rgba(151, 71, 255, 0.1)",
                  },
                },
              },
            }}
          />
          <TextField
            label="Email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
            type="email"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EmailIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                transition: "all 0.3s ease",
                "&:hover": {
                  "& fieldset": {
                    borderColor: "rgba(151, 71, 255, 0.5)",
                  },
                },
                "&.Mui-focused": {
                  "& fieldset": {
                    borderColor: "#9747FF",
                    boxShadow: "0 0 0 2px rgba(151, 71, 255, 0.1)",
                  },
                },
              },
            }}
          />
          <TextField
            label="Company"
            name="company"
            value={form.company}
            onChange={handleChange}
            required
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <BusinessIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                transition: "all 0.3s ease",
                "&:hover": {
                  "& fieldset": {
                    borderColor: "rgba(151, 71, 255, 0.5)",
                  },
                },
                "&.Mui-focused": {
                  "& fieldset": {
                    borderColor: "#9747FF",
                    boxShadow: "0 0 0 2px rgba(151, 71, 255, 0.1)",
                  },
                },
              },
            }}
          />
          <TextField
            label="Title"
            name="title"
            value={form.title}
            onChange={handleChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <WorkIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                transition: "all 0.3s ease",
                "&:hover": {
                  "& fieldset": {
                    borderColor: "rgba(151, 71, 255, 0.5)",
                  },
                },
                "&.Mui-focused": {
                  "& fieldset": {
                    borderColor: "#9747FF",
                    boxShadow: "0 0 0 2px rgba(151, 71, 255, 0.1)",
                  },
                },
              },
            }}
          />
          <TextField
            label="Industry"
            name="industry"
            value={form.industry}
            onChange={handleChange}
            helperText="e.g., Technology, Healthcare, Finance"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <CategoryIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                transition: "all 0.3s ease",
                "&:hover": {
                  "& fieldset": {
                    borderColor: "rgba(151, 71, 255, 0.5)",
                  },
                },
                "&.Mui-focused": {
                  "& fieldset": {
                    borderColor: "#9747FF",
                    boxShadow: "0 0 0 2px rgba(151, 71, 255, 0.1)",
                  },
                },
              },
            }}
          />
          <TextField
            select
            label="Company Size"
            name="companySize"
            value={form.companySize}
            onChange={handleChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <GroupsIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                transition: "all 0.3s ease",
                "&:hover": {
                  "& fieldset": {
                    borderColor: "rgba(151, 71, 255, 0.5)",
                  },
                },
                "&.Mui-focused": {
                  "& fieldset": {
                    borderColor: "#9747FF",
                    boxShadow: "0 0 0 2px rgba(151, 71, 255, 0.1)",
                  },
                },
              },
            }}
          >
            {companySizes.map((size) => (
              <MenuItem key={size.value} value={size.value}>
                {size.label}
              </MenuItem>
            ))}
          </TextField>

          <Button
            onClick={handleSubmit}
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{
              mt: 2,
              py: 1.5,
              background: "linear-gradient(145deg, #9747FF 0%, #7B2FFF 100%)",
              transition: "all 0.3s ease",
              "&:hover": {
                background: "linear-gradient(145deg, #A55FFF 0%, #8B3FFF 100%)",
                transform: "translateY(-1px)",
                boxShadow: "0 4px 20px rgba(151, 71, 255, 0.3)",
              },
              "&:disabled": {
                background: "rgba(151, 71, 255, 0.5)",
              },
            }}
          >
            {loading ? <CircularProgress size={24} /> : "Continue"}
          </Button>

          {error && (
            <Typography
              color="error"
              variant="body2"
              sx={{
                animation: "fadeIn 0.3s ease forwards",
              }}
            >
              {error}
            </Typography>
          )}
        </Box>
      </Paper>
    </Box>
  );
}
