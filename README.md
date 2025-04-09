# Seeker

Agent-powered job search assistant.

## Project Overview

Seeker is a modern job search tool that leverages AI agents to streamline the job hunting process. The project consists of a Next.js frontend and a Flask backend.

## Architecture

### Components

- **Frontend**: Next.js application with TypeScript
- **Backend**: Flask REST API with WebSocket support
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT-4 for natural language processing and tool calling
- **External APIs**: SerpAPI for job search and company research

### Key Features

- Real-time chat interface for AI-powered job search assistance
- Dynamic email sequence generation for outreach to potential employers
- Job search and company analysis capabilities
- Personalized outreach message generation for networking and applications
- WebSocket-based real-time updates
- Job lead tracking and management
- Application status monitoring

## Database Schema

### Core Models

- **User**: Stores job seeker information and preferences
- **Session**: Represents a chat session between user and AI
- **Message**: Stores chat messages within a session
- **SequenceStep**: Contains individual steps in an outreach sequence
- **JobLead**: Stores information about potential job opportunities

### Relationships

- User has many Sessions (1:N)
- Session has many Messages (1:N)
- Session has many SequenceSteps (1:N)

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- OpenAI API key
- SerpAPI key

## Installation

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   Inside /backend

   Create `.env` file and add:

```
OPENAI_API_KEY=<your-openai-key>
FLASK_APP=app:create_app
FLASK_ENV=development
SERPAPI_KEY=<your-serp-key>
```

5. Initialize the database:

   From /backend run the following command -

   ```bash
   python3 src/init_db.py
   ```

   This will create a SQLite database file (`seeker.db`) in your backend directory with all necessary tables.

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

## Running the Application

### Start the Backend

1. Make sure you're in the backend/src directory with the virtual environment activated
2. Run the Flask application:
   ```bash
    python3 run.py
   ```
   The backend will start on `http://localhost:5001`

### Start the Frontend

1. In a new terminal, navigate to the frontend directory

2. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will start on `http://localhost:3000`

## Development

- Backend API documentation is available at `http://localhost:5001/api/docs`
- Frontend development server includes hot reloading
- Use `npm run lint` to check for frontend code style issues
- The SQLite database file (`seeker.db`) will be created automatically when you run `init_db.py`

## Troubleshooting

### Common Issues

1. **Database Connection Issues**

   - Ensure the SQLite database file exists
   - Check database permissions
   - Verify environment variables are set correctly

2. **API Key Issues**

   - Verify OpenAI and SerpAPI keys are valid
   - Check environment variables are loaded properly

3. **WebSocket Connection Problems**
   - Ensure CORS settings are correct
   - Check if the frontend is using the correct WebSocket URL
