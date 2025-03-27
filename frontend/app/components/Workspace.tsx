import { Paper, Typography, Box, Fade } from "@mui/material";
import { SequenceStep } from "../hooks/useChat";

interface WorkspaceProps {
  sequence: SequenceStep[];
}

export default function Workspace({ sequence }: WorkspaceProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 4,
        height: "100%",
        overflowY: "auto",
        background: "transparent",
      }}
    >
      <Typography
        variant="h5"
        sx={{
          mb: 4,
          fontWeight: 600,
          background: "linear-gradient(145deg, #9747FF 0%, #7B2FFF 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
        }}
      >
        Generated Sequence
      </Typography>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {sequence.length > 0 ? (
          sequence.map((step, index) => (
            <Fade
              key={step.step_number}
              in
              timeout={300}
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  background: "rgba(255, 255, 255, 0.05)",
                  borderRadius: "12px",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  transition: "all 0.3s ease",
                  "&:hover": {
                    background: "rgba(255, 255, 255, 0.08)",
                    transform: "translateY(-2px)",
                  },
                }}
              >
                <Typography
                  variant="subtitle1"
                  sx={{
                    mb: 1,
                    fontWeight: 600,
                    color: "#9747FF",
                  }}
                >
                  Step {step.step_number}
                </Typography>
                <Typography
                  variant="body1"
                  sx={{
                    color: "text.primary",
                    lineHeight: 1.6,
                  }}
                >
                  {step.content}
                </Typography>
              </Paper>
            </Fade>
          ))
        ) : (
          <Typography
            variant="body1"
            sx={{
              color: "text.secondary",
              textAlign: "center",
              py: 4,
            }}
          >
            Your generated sequences will appear here.
          </Typography>
        )}
      </Box>
    </Paper>
  );
}
