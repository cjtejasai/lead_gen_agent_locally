# Lyncsea - Proper Clean Architecture

## 🎯 Goals
1. **Separation of concerns** - Backend = code only, no data
2. **Clear organization** - Everything in its logical place
3. **Single source of truth** - One requirements.txt, one .env
4. **Professional structure** - Like a real production app

---

## 📁 Target Structure

```
lyncsea/
│
├── backend/                      # Pure backend code - NO DATA
│   ├── app/
│   │   ├── api/                  # API endpoints
│   │   ├── core/                 # Config, database
│   │   ├── models/               # Database models
│   │   ├── services/             # Business logic
│   │   └── main.py
│   ├── migrations/               # SQL migrations
│   └── requirements.txt          # Backend dependencies ONLY
│
├── frontend/                     # Frontend - stays as is
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── package.json
│
├── agents/                       # 🆕 Agent scripts (organized)
│   ├── __init__.py
│   ├── lead_generator.py         # Renamed from lyncsea_crew.py
│   ├── event_discoverer.py       # Renamed from event_discovery.py
│   ├── tools/                    # Shared agent tools
│   │   ├── __init__.py
│   │   ├── email_sender.py
│   │   ├── file_saver.py
│   │   └── web_search.py
│   └── requirements.txt          # Agent dependencies (CrewAI, etc.)
│
├── data/                         # 🆕 All application data
│   ├── recordings/               # Audio files
│   ├── transcripts/              # Transcripts
│   ├── leads/                    # Generated leads JSON
│   └── events/                   # Discovered events JSON
│
├── logs/                         # 🆕 All logs in one place
│   ├── backend.log
│   ├── agents.log
│   └── events.log
│
├── infra/                        # 🆕 Infrastructure & deployment
│   ├── docker/
│   │   └── docker-compose.yml
│   ├── deploy/
│   │   ├── ec2_setup.sh
│   │   └── nginx.conf
│   └── scripts/
│       ├── backup_db.sh
│       └── setup_env.sh
│
├── docs/                         # 🆕 All documentation
│   ├── README.md                 # Main readme
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── AGENTS.md                 # Agent system docs
│   └── API.md                    # API documentation
│
├── .env                          # Single environment file
├── .gitignore
├── requirements.txt              # Main dependencies (combined)
└── README.md                     # Quick start
```

---

## 🔧 Changes Needed

### 1. Reorganize Agent Files
**Current:**
- `lyncsea_crew.py` (root)
- `event_discovery.py` (root)

**New:**
- `agents/lead_generator.py` (better name)
- `agents/event_discoverer.py` (better name)
- `agents/tools/` (shared utilities)

### 2. Consolidate Data Folders
**Current:**
- `recordings/` (root)
- `transcripts/` (root)
- `leads_data/` (root)
- `discovered_events/` (root)

**New:**
- `data/recordings/`
- `data/transcripts/`
- `data/leads/`
- `data/events/`

### 3. Centralize Logs
**Current:**
- `lyncsea_agent.log` (root)
- `lyncsea_event_discovery.log` (root)
- Logs might be in backend too

**New:**
- `logs/backend.log`
- `logs/agents.log`
- `logs/events.log`

### 4. Consolidate Requirements
**Current:**
- `requirements.txt` (root - main deps)
- `agent_requirements.txt` (root - agent deps)
- Backend might have its own

**Options:**
**Option A: Single file** (Simpler)
- `requirements.txt` with all dependencies

**Option B: Separate by purpose** (Better for production)
- `backend/requirements.txt` - FastAPI, SQLAlchemy, etc.
- `agents/requirements.txt` - CrewAI, OpenAI, etc.
- `requirements.txt` (root) - Install script that calls both

### 5. Clean Up Environment Files
**Current:**
- `.env` (root)
- Might have `.env` in backend
- `.env.local` in frontend

**New:**
- `.env` (root) - Single source of truth
- Backend reads from `../.env`
- Frontend uses `.env.local` (Next.js standard)

### 6. Move Infrastructure Files
**Current:**
- `docker-compose.yml` (root)
- `.pem` files (root)
- Deployment docs scattered

**New:**
- `infra/docker/docker-compose.yml`
- `infra/keys/` (for .pem files, gitignored)
- `docs/DEPLOYMENT.md`

### 7. Organize Documentation
**Current:**
- `README.md`
- `CLAUDE.md`
- `EC2_DEPLOYMENT_GUIDE.md`
- `CLEANUP_PLAN.md`
- `CLEANUP_COMPLETE.md`

**New:**
- `README.md` (quick start)
- `docs/AGENTS.md` (agent system)
- `docs/DEPLOYMENT.md` (EC2 deployment)
- Archive cleanup docs

---

## 🚀 Implementation Plan

### Phase 1: Create New Directory Structure
```bash
mkdir -p agents/tools
mkdir -p data/{recordings,transcripts,leads,events}
mkdir -p logs
mkdir -p infra/{docker,deploy,scripts,keys}
mkdir -p docs
```

### Phase 2: Move Agent Files
```bash
# Move and rename agent scripts
mv lyncsea_crew.py agents/lead_generator.py
mv event_discovery.py agents/event_discoverer.py

# Update imports inside agent files
# Update references in backend/app/services/
```

### Phase 3: Consolidate Data
```bash
# Move all data folders
mv recordings/* data/recordings/ 2>/dev/null
mv transcripts/* data/transcripts/ 2>/dev/null
mv leads_data/* data/leads/ 2>/dev/null
mv discovered_events/* data/events/ 2>/dev/null

# Remove old empty folders
rmdir recordings transcripts leads_data discovered_events
```

### Phase 4: Centralize Logs
```bash
# Move log files
mv lyncsea_agent.log logs/agents.log
mv lyncsea_event_discovery.log logs/events.log

# Update log paths in code
# agents/lead_generator.py -> logs/agents.log
# agents/event_discoverer.py -> logs/events.log
```

### Phase 5: Reorganize Requirements
```bash
# Move agent requirements
mv agent_requirements.txt agents/requirements.txt

# Keep main requirements.txt in root
# Backend will have its own in backend/requirements.txt
```

### Phase 6: Move Infrastructure
```bash
# Move docker files
mv docker-compose.yml infra/docker/

# Move .pem files
mv *.pem infra/keys/
echo "infra/keys/" >> .gitignore
```

### Phase 7: Organize Docs
```bash
# Move documentation
mv EC2_DEPLOYMENT_GUIDE.md docs/DEPLOYMENT.md
mv CLAUDE.md docs/AGENTS.md

# Archive cleanup docs
mv CLEANUP_*.md archive_old/
```

---

## 📝 Code Updates Needed

### 1. Update Agent Imports in Backend
**File:** `backend/app/services/lead_generation.py`
```python
# OLD
from lyncsea_crew import LyncseaCrew

# NEW
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'agents'))
from lead_generator import LeadGenerator
```

### 2. Update Log Paths in Agents
**File:** `agents/lead_generator.py`
```python
# OLD
logging.FileHandler('lyncsea_agent.log')

# NEW
logging.FileHandler('logs/agents.log')
```

### 3. Update Data Paths
**All files that reference:**
- `recordings/` → `data/recordings/`
- `transcripts/` → `data/transcripts/`
- `leads_data/` → `data/leads/`
- `discovered_events/` → `data/events/`

### 4. Update Docker Compose Path
**File:** `docs/DEPLOYMENT.md`
```bash
# OLD
docker-compose up -d

# NEW
docker-compose -f infra/docker/docker-compose.yml up -d
```

---

## 🎯 Benefits of New Structure

1. ✅ **Backend is pure code** - No data files
2. ✅ **Clear separation** - agents/, data/, logs/, infra/
3. ✅ **Better names** - lead_generator.py, event_discoverer.py (self-documenting)
4. ✅ **Professional** - Follows industry standards
5. ✅ **Scalable** - Easy to add more agents, services
6. ✅ **Maintainable** - Everything has its place
7. ✅ **Git-friendly** - data/ and logs/ can be gitignored

---

## 🚨 Files to Update After Restructure

### Backend Files:
- `backend/app/services/lead_generation.py` - Import path
- `backend/app/services/event_discovery_service.py` - Import path (if exists)
- `backend/app/core/config.py` - Data folder paths

### Agent Files:
- `agents/lead_generator.py` - Log path, data paths
- `agents/event_discoverer.py` - Log path, data paths

### Config Files:
- `.gitignore` - Add data/, logs/, infra/keys/
- Docker compose - Update volume paths

### Documentation:
- `README.md` - Update quick start
- `docs/DEPLOYMENT.md` - Update paths
- `docs/AGENTS.md` - Update file references

---

## 📊 Comparison

### Before (Current - After basic cleanup):
```
lyncsea/
├── backend/
├── frontend/
├── lyncsea_crew.py ❌ (confusing name, wrong location)
├── event_discovery.py ❌ (wrong location)
├── recordings/ ❌ (data in root)
├── transcripts/ ❌ (data in root)
├── leads_data/ ❌ (data in root)
├── lyncsea_agent.log ❌ (logs in root)
├── requirements.txt ❌ (mixed deps)
├── agent_requirements.txt ❌ (duplicate)
└── docker-compose.yml ❌ (infra in root)
```

### After (Proper Structure):
```
lyncsea/
├── backend/          ✅ (pure code)
├── frontend/         ✅ (pure code)
├── agents/           ✅ (organized, clear names)
│   ├── lead_generator.py
│   └── event_discoverer.py
├── data/             ✅ (all data together)
│   ├── recordings/
│   ├── transcripts/
│   ├── leads/
│   └── events/
├── logs/             ✅ (all logs together)
├── infra/            ✅ (infrastructure separate)
│   └── docker/
├── docs/             ✅ (documentation organized)
└── requirements.txt  ✅ (single source)
```

---

## ⚡ Quick Start After Restructure

```bash
# Clone repo
git clone <repo>
cd lyncsea

# Install dependencies
pip install -r requirements.txt
cd agents && pip install -r requirements.txt && cd ..

# Setup environment
cp .env.example .env
# Edit .env with your keys

# Start database
docker-compose -f infra/docker/docker-compose.yml up -d

# Run migrations
cd backend && alembic upgrade head && cd ..

# Start backend
cd backend && uvicorn app.main:app --reload

# Start frontend
cd frontend && npm install && npm run dev
```

---

## 🎯 Next Steps

1. Review this structure
2. Confirm changes
3. Execute reorganization
4. Update all imports and paths
5. Test everything
6. Commit with proper structure

Ready to proceed with the reorganization?