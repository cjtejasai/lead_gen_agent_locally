# Getting Started with Ayka

Welcome to Ayka, your AI-powered lead generation platform!

## What You've Got

A complete, production-ready platform with:
- **Backend API** (FastAPI + Python)
- **Frontend Web App** (Next.js + TypeScript)
- **AI Agents** (LLM-powered analysis)
- **Graph Database** (Neo4j for smart matching)
- **Calendar Integration** (Google Calendar)
- **Speech-to-Text** (AssemblyAI/Whisper)

## Quick Start (5 minutes)

### 1. Run the Quick Start Script

```bash
./quick-start.sh
```

This will:
- Start Docker containers (PostgreSQL, Neo4j, Redis)
- Create environment files
- Show you next steps

### 2. Add Your API Keys

Edit `backend/.env` and add:
```env
OPENAI_API_KEY=sk-your-key-here
ASSEMBLYAI_API_KEY=your-key-here
```

### 3. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Start Frontend

In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

### 5. Open Your Browser

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

## What Can You Do?

### Upload & Analyze Recordings
1. Go to Dashboard
2. Drag & drop an audio file (MP3, WAV, M4A)
3. Wait for AI analysis
4. See extracted interests, topics, and intents

### Discover Matches
1. Check "Top Matches" feed
2. See why each match is relevant
3. Click "Connect" to schedule a meeting
4. Calendar integration creates Google Meet link

### View Your Network
1. Go to "My Interests"
2. See your interest graph
3. Explore connections and relationships

## Project Structure

```
ayka_lead_gen/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # REST API endpoints
│   │   ├── agents/      # LLM agents
│   │   ├── services/    # Business logic
│   │   └── main.py      # FastAPI app
│   └── requirements.txt
│
├── frontend/            # Next.js frontend
│   ├── app/
│   │   ├── dashboard/   # Main dashboard
│   │   └── page.tsx     # Landing page
│   └── package.json
│
└── docker-compose.yml   # Database services
```

## Key Files to Know

### Documentation
- `README.md` - Project overview
- `ARCHITECTURE.md` - System design & data flow
- `IMPLEMENTATION_GUIDE.md` - Detailed setup
- `PROJECT_SUMMARY.md` - Complete feature list

### Backend Key Files
- `backend/app/main.py` - FastAPI application
- `backend/app/core/config.py` - Configuration
- `backend/app/agents/orchestrator.py` - AI agent system
- `backend/app/services/matching_engine.py` - Matching algorithm
- `backend/app/core/neo4j_schema.py` - Graph schema

### Frontend Key Files
- `frontend/app/page.tsx` - Landing page
- `frontend/app/dashboard/page.tsx` - Main dashboard
- `frontend/app/layout.tsx` - Root layout
- `frontend/app/globals.css` - Global styles

## Common Tasks

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### Test Speech-to-Text

```python
from app.services.speech_to_text import SpeechToTextService

stt = SpeechToTextService(provider="assemblyai")
result = stt.transcribe("audio.mp3", speaker_diarization=True)
print(result["full_transcript"])
```

### Test AI Agents

```python
from app.agents.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
results = orchestrator.analyze_recording(
    transcript="I'm looking for AI startup investments...",
    user_category="ceo_investor"
)
print(results)
```

### Test Matching

```python
from app.services.matching_engine import MatchingEngine

engine = MatchingEngine()
matches = engine.find_matches(
    user_email="user@example.com",
    min_score=50.0,
    limit=10
)
print(f"Found {len(matches)} matches")
```

## Troubleshooting

### Services Not Starting?

```bash
# Check Docker status
docker-compose ps

# View logs
docker-compose logs postgres
docker-compose logs neo4j
docker-compose logs redis

# Restart services
docker-compose restart
```

### Backend Errors?

```bash
# Check if all dependencies are installed
cd backend
pip install -r requirements.txt

# Verify environment variables
cat .env

# Check if ports are available
lsof -i :8000
```

### Frontend Errors?

```bash
# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check if port is available
lsof -i :3000
```

### Database Connection Issues?

```bash
# Test PostgreSQL
docker exec -it ayka_postgres psql -U postgres -d ayka_leadgen

# Test Neo4j (in browser)
open http://localhost:7474

# Test Redis
docker exec -it ayka_redis redis-cli ping
```

## Next Steps

### 1. Customize the Platform
- Modify matching algorithm weights
- Add new user categories
- Customize UI colors and branding
- Add more AI agents for specialized analysis

### 2. Add Authentication
- Implement JWT token generation
- Add user registration flow
- Protect API endpoints
- Add OAuth login (Google, GitHub)

### 3. Deploy to Production
- Set up CI/CD pipeline
- Deploy backend to Railway/Render
- Deploy frontend to Vercel
- Use managed databases (Neo4j Aura, AWS RDS)

### 4. Hardware Integration
- Connect with pendant device
- Implement real-time streaming
- Add mobile app for device management

## Learning Resources

### FastAPI
- Official Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### Next.js
- Official Docs: https://nextjs.org/docs
- Learn Next.js: https://nextjs.org/learn

### Neo4j
- Graph Database Concepts: https://neo4j.com/developer/graph-database/
- Cypher Query Language: https://neo4j.com/developer/cypher/

### LangChain (for LLM agents)
- Docs: https://python.langchain.com/docs/get_started/introduction

## Get Help

- Check the documentation files
- Review API docs at http://localhost:8000/docs
- Look at code comments
- Search for TODOs in the codebase

## Development Tips

### Backend Development
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests (when added)
pytest

# Format code
black app/
```

### Frontend Development
```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Database Management
```bash
# Access PostgreSQL
docker exec -it ayka_postgres psql -U postgres -d ayka_leadgen

# Access Neo4j shell
docker exec -it ayka_neo4j cypher-shell -u neo4j -p your-password

# Access Redis
docker exec -it ayka_redis redis-cli
```

## Project Status

✅ **Completed**:
- System architecture
- Backend API structure
- AI agent system
- Graph database schema
- Matching algorithm
- Frontend UI/UX
- Calendar integration
- Docker setup

🚧 **In Progress**:
- User authentication
- Database migrations
- Unit tests
- Hardware integration

📋 **Planned**:
- Real-time processing
- Mobile app
- Advanced analytics
- Multi-language support

## Success Metrics

When everything is working, you should see:
- ✅ Backend API responding at http://localhost:8000
- ✅ Frontend loading at http://localhost:3000
- ✅ Neo4j accessible at http://localhost:7474
- ✅ All Docker containers running
- ✅ No errors in terminal logs

## Have Fun!

You now have a powerful AI platform. Experiment, customize, and build something amazing!

For questions or issues, check:
1. `IMPLEMENTATION_GUIDE.md` for setup details
2. `ARCHITECTURE.md` for system design
3. `PROJECT_SUMMARY.md` for feature overview

Happy coding! 🚀
