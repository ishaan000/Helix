import { Paper, Typography, Box } from "@mui/material";
import { SequenceStep } from "../hooks/useChat";

interface WorkspaceProps {
  sequence: SequenceStep[];
}

export default function Workspace({ sequence }: WorkspaceProps) {
  return (
    <Paper
      elevation={3}
      square
      sx={{ p: 2, height: "100%", overflowY: "auto" }}
    >
      <Typography variant="h6" gutterBottom>
        🧾 Generated Sequence
      </Typography>
      <Box sx={{ mt: 2 }}>
        {sequence.length > 0 ? (
          sequence.map((step) => (
            <Paper
              key={step.step_number}
              sx={{ p: 2, mb: 1 }}
              variant="outlined"
            >
              <Typography variant="subtitle2">
                Step {step.step_number}
              </Typography>
              <Typography variant="body2">{step.content}</Typography>
            </Paper>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            Your generated sequences will appear here.
          </Typography>
        )}
      </Box>
    </Paper>
  );
}
