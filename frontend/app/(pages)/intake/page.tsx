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
} from "@mui/icons-material";

const jobTypes = [
  { value: "fullTime", label: "Full-time" },
  { value: "partTime", label: "Part-time" },
  { value: "contract", label: "Contract" },
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
];

const jobLevels = [
  { value: "entry", label: "Entry Level" },
  { value: "mid", label: "Mid Level" },
  { value: "senior", label: "Senior Level" },
  { value: "manager", label: "Management" },
  { value: "executive", label: "Executive" },
];

export default function IntakePage() {
  const router = useRouter();
  const { register, loading, error } = useRegister();

  const [form, setForm] = useState({
    name: "",
    email: "",
    current_company: "",
    title: "",
    industry: "",
    job_types: [],
    target_companies: "",
    target_locations: "",
    years_experience: "",
    skills: "",
    job_level: "mid",
  });

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleMultiSelectChange = (name: string) => (event: React.ChangeEvent<{ value: unknown }>) => {
    const { value } = event.target;
    setForm((prev) => ({ ...prev, [name]: typeof value === 'string' ? value.split(',') : value }));
  };

  const handleSubmit = async () => {
    // Format the data to match the backend expectations
    const formattedData = {
      name: form.name,
      email: form.email,
      current_company: form.current_company,
      title: form.title,
      industry: form.industry,
      preferences: {
        jobTypes: Array.isArray(form.job_types) ? form.job_types : [form.job_types],
        targetCompanies: form.target_companies.split(',').map(c => c.trim()).filter(c => c),
        targetLocations: form.target_locations.split(',').map(l => l.trim()).filter(l => l),
        yearsExperience: parseInt(form.years_experience) || 0,
        skills: form.skills.split(',').map(s => s.trim()).filter(s => s),
        jobLevel: form.job_level
      }
    };
    
    const userId = await register(formattedData);
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
        Let Helix Help Your Job Search
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
        I&apos;m Helix, your AI job search assistant. Share a bit about yourself and your career goals so I can help you connect with the right opportunities and people.
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
            label="Current or Previous Company"
            name="current_company"
            value={form.current_company}
            onChange={handleChange}
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
            label="Current or Target Job Title"
            name="title"
            value={form.title}
            onChange={handleChange}
            required
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
            required
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
            label="Job Types"
            name="job_types"
            value={form.job_types}
            onChange={handleMultiSelectChange("job_types")}
            SelectProps={{
              multiple: true
            }}
            helperText="Select all that apply"
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
            {jobTypes.map((type) => (
              <MenuItem key={type.value} value={type.value}>
                {type.label}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Target Companies"
            name="target_companies"
            value={form.target_companies}
            onChange={handleChange}
            helperText="Comma-separated list of companies you're interested in"
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
            label="Preferred Locations"
            name="target_locations"
            value={form.target_locations}
            onChange={handleChange}
            helperText="Comma-separated list (e.g., Remote, San Francisco, New York)"
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
            label="Years of Experience"
            name="years_experience"
            type="number"
            value={form.years_experience}
            onChange={handleChange}
            InputProps={{
              inputProps: { min: 0 }
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
            label="Key Skills"
            name="skills"
            value={form.skills}
            onChange={handleChange}
            helperText="Comma-separated list of your top skills"
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
            label="Job Level"
            name="job_level"
            value={form.job_level}
            onChange={handleChange}
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
            {jobLevels.map((level) => (
              <MenuItem key={level.value} value={level.value}>
                {level.label}
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
