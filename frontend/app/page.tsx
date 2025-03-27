"use client";

import { Grid, Paper, Typography } from "@mui/material";

export default function HomePage() {
  return (
    <Grid container sx={{ height: "100vh" }}>
      <Grid
        item
        xs={4}
        component={Paper as React.ElementType}
        elevation={3}
        square
        sx={{ p: 2, borderRight: "1px solid #eee" }}
      >
        <Typography variant="h6" gutterBottom>
          🧠 Chat (Coming Soon)
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This is where your AI conversations will appear.
        </Typography>
      </Grid>

      <Grid
        item
        xs={8}
        component={Paper as React.ElementType}
        elevation={3}
        square
        sx={{ p: 2 }}
      >
        <Typography variant="h6" gutterBottom>
          🧾 Outreach Workspace (Coming Soon)
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Generated sequences will be editable here.
        </Typography>
      </Grid>
    </Grid>
  );
}
