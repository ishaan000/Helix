# Helix

Agent-powered recruiting tool.

## Project Overview

Helix is a modern recruiting tool that leverages AI agents to streamline the recruitment process. The project consists of a Next.js frontend and a Flask backend.

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
   This will create a SQLite database file (`helix.db`) in your backend directory with all necessary tables.

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
- The SQLite database file (`helix.db`) will be created automatically when you run `init_db.py`
