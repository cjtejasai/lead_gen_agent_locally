# Ayka Lead Generation Platform

An AI-powered lead generation platform that processes audio/video recordings from wearable devices at events to identify collaboration opportunities using LLMs and graph-based interest matching.

## Features

- **Audio/Video Processing**: Automated speech-to-text conversion with speaker diarization
- **AI-Powered Analysis**: Multi-agent LLM system for extracting insights, interests, and intent
- **Graph-Based Matching**: Neo4j-powered interest graph for finding complementary connections
- **Smart Lead Generation**: Automated matching algorithm with LLM-based scoring
- **Calendar Integration**: One-click scheduling for discovered opportunities
- **Modern UI/UX**: Classy, responsive interface built with Next.js and Tailwind CSS

## Project Structure

```
ayka_lead_gen/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Core configuration and utilities
│   │   ├── models/         # Data models and schemas
│   │   ├── services/       # Business logic services
│   │   └── agents/         # LLM-based agents
│   └── tests/              # Backend tests
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app router
│   ├── components/         # React components
│   ├── lib/                # Utilities and helpers
│   └── public/             # Static assets
├── docs/                   # Documentation
└── docker-compose.yml      # Local development setup
```

## Tech Stack

### Backend
- FastAPI (Python)
- Neo4j (Graph Database)
- PostgreSQL (Relational Database)
- Redis (Caching & Task Queue)
- Celery (Background Jobs)
- OpenAI/Anthropic APIs (LLM)
- Whisper/AssemblyAI (Speech-to-Text)

### Frontend
- Next.js 14+
- TypeScript
- Tailwind CSS + shadcn/ui
- React Query
- Zustand (State Management)
- D3.js (Graph Visualization)

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Neo4j Database
- OpenAI/Anthropic API Key

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd ayka_lead_gen
```

2. Set up backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
```

3. Set up frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # Configure your environment variables
```

4. Start services with Docker Compose
```bash
docker-compose up -d
```

5. Run migrations
```bash
cd backend
alembic upgrade head
```

6. Start development servers

Backend:
```bash
cd backend
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

## User Categories

1. **CEO / Investor**: Looking for investment opportunities, partnerships, strategic connections
2. **Students**: Looking for internships, learning opportunities, mentorship
3. **General**: Various collaboration needs (hiring, partnerships, services, etc.)

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system architecture and data flow.

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

Proprietary - All rights reserved

## Contact

For questions or support, contact the development team.
