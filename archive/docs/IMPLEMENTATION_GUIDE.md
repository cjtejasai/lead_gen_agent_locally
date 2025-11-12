# Ayka Lead Generation Platform - Implementation Guide

## Overview

This guide will help you get the Ayka platform up and running. The platform consists of:
- **Backend**: FastAPI with Neo4j graph database, PostgreSQL, Redis
- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **AI Services**: OpenAI/Anthropic LLMs, speech-to-text processing
- **Calendar Integration**: Google Calendar API

## Prerequisites

1. **Python 3.11+**
2. **Node.js 20+**
3. **Docker & Docker Compose** (for local development)
4. **API Keys**:
   - OpenAI API Key
   - Anthropic API Key (optional)
   - AssemblyAI API Key (for speech-to-text)
   - Google Cloud Project with Calendar API enabled

## Step 1: Environment Setup

### Backend Environment

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` and add your API keys:
```env
SECRET_KEY=your-secret-key-generate-a-random-string
OPENAI_API_KEY=sk-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
ASSEMBLYAI_API_KEY=your-assemblyai-api-key
NEO4J_PASSWORD=change-this-password
# ... other configuration
```

### Frontend Environment

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env.local
```

4. Configure frontend environment:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 2: Database Setup

### Using Docker Compose (Recommended for Development)

1. Start all services:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Neo4j on ports 7474 (HTTP) and 7687 (Bolt)
- Redis on port 6379

2. Verify services are running:
```bash
docker-compose ps
```

3. Access Neo4j Browser:
- URL: http://localhost:7474
- Username: neo4j
- Password: your-neo4j-password (from .env)

### Manual Setup (Alternative)

If you prefer to install databases manually:

1. **PostgreSQL**:
```bash
# Create database
createdb ayka_leadgen
```

2. **Neo4j**:
- Download from https://neo4j.com/download/
- Install APOC and GDS plugins
- Start Neo4j server

3. **Redis**:
```bash
# Install and start Redis
brew install redis  # macOS
redis-server
```

## Step 3: Initialize Neo4j Schema

1. With Neo4j running, initialize the schema:
```bash
cd backend
python -c "
from app.core.neo4j_schema import CREATE_CONSTRAINTS, CREATE_INDEXES
from neo4j import GraphDatabase
from app.core.config import settings

driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

with driver.session() as session:
    for query in CREATE_CONSTRAINTS:
        print(f'Creating constraint...')
        session.run(query)

    for query in CREATE_INDEXES:
        print(f'Creating index...')
        session.run(query)

driver.close()
print('Neo4j schema initialized successfully!')
"
```

## Step 4: Run Database Migrations

```bash
cd backend
alembic upgrade head
```

## Step 5: Start Development Servers

### Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Celery Worker (for background tasks)

In a separate terminal:
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

### Frontend

In another terminal:
```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:3000

## Step 6: Test the Platform

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Test Speech-to-Text Service

Create a test script `test_stt.py`:
```python
from app.services.speech_to_text import SpeechToTextService

# Initialize service
stt = SpeechToTextService(provider="assemblyai")

# Test with a sample audio file
result = stt.transcribe("path/to/your/audio.mp3", speaker_diarization=True)

print("Transcript:", result["full_transcript"])
print("Speakers:", result["num_speakers"])
print("Segments:", len(result["segments"]))
```

### 3. Test LLM Agents

```python
from app.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Sample transcript
transcript = """
I'm looking for investors who are interested in AI startups.
We're building a SaaS platform for small businesses.
Our revenue is growing 20% month over month.
"""

# Analyze
results = orchestrator.analyze_recording(
    transcript=transcript,
    user_category="ceo_investor"
)

print("Analysis:", results)
```

### 4. Test Matching Engine

```python
from app.services.matching_engine import MatchingEngine

engine = MatchingEngine()

# Find matches for a user
matches = engine.find_matches(
    user_email="user@example.com",
    min_score=50.0,
    limit=10
)

print(f"Found {len(matches)} matches")
for match in matches:
    print(f"- {match['matched_name']}: {match['score']['total_score']}%")

engine.close()
```

## Step 7: Google Calendar Setup

1. Create a Google Cloud Project:
   - Go to https://console.cloud.google.com
   - Create a new project

2. Enable Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. Create OAuth2 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - http://localhost:8000/auth/google/callback
     - http://localhost:3000/auth/google/callback

4. Download credentials and update `.env`:
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

## Step 8: AWS S3 Setup (for file storage)

1. Create an S3 bucket:
```bash
aws s3 mb s3://ayka-recordings
```

2. Configure CORS for the bucket:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST"],
        "AllowedOrigins": ["http://localhost:3000"],
        "ExposeHeaders": []
    }
]
```

3. Update `.env` with AWS credentials:
```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BUCKET_NAME=ayka-recordings
AWS_REGION=us-east-1
```

## Common Issues & Solutions

### Issue: Neo4j connection failed

**Solution**:
- Verify Neo4j is running: `docker-compose ps`
- Check credentials in `.env`
- Try connecting via Neo4j Browser at http://localhost:7474

### Issue: Port already in use

**Solution**:
```bash
# Find process using the port
lsof -i :8000  # or :3000, :5432, etc.

# Kill the process
kill -9 <PID>
```

### Issue: Module not found errors

**Solution**:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: LLM API rate limits

**Solution**:
- Check your API key quotas
- Implement rate limiting in production
- Consider using caching for repeated queries

## Production Deployment

### Backend Deployment (example using Railway/Render)

1. Set environment variables in your hosting platform
2. Use `gunicorn` instead of `uvicorn`:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment (Vercel)

1. Push to GitHub
2. Import project to Vercel
3. Set environment variables
4. Deploy

### Database Deployment

- **PostgreSQL**: Railway, Supabase, or AWS RDS
- **Neo4j**: Neo4j Aura (managed cloud service)
- **Redis**: Upstash or AWS ElastiCache

## Next Steps

1. **Implement Authentication**: Add JWT-based authentication
2. **Add Tests**: Write unit and integration tests
3. **Monitoring**: Set up Sentry for error tracking
4. **Analytics**: Add user analytics and metrics
5. **Mobile App**: Build mobile app for pendant device
6. **Hardware Integration**: Connect with pendant hardware

## Support

For issues or questions:
- Check the [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Review API documentation at http://localhost:8000/docs
- Open an issue on GitHub

## License

Proprietary - All rights reserved
