# Lyncsea Project Cleanup & Reorganization Plan

## 📋 Current Status
Project: `ayka_lead_gen` → Rename to `lyncsea`
Last Updated: 2025-11-15

---

## 🎯 PRODUCTION FILES (KEEP & MAINTAIN)

### Core Agent Files (Rename from ayka → lyncsea)
- ✅ `ayka_crew.py` → **`lyncsea_crew.py`** (Lead generation multi-agent)
- ✅ `event_discovery.py` → **KEEP** (Event discovery agent)
- ⚠️ `ayka_agent.py` → **REVIEW** (12KB - seems duplicate of ayka_crew.py?)
- ❌ `shruti_agent.py` → **ARCHIVE** (Old agent, not used in production)

### Backend (KEEP - Essential)
```
backend/
  ├── app/
  │   ├── api/                  # All API endpoints ✅
  │   ├── core/                 # Config, database ✅
  │   ├── models/               # Database models ✅
  │   ├── services/             # Business logic ✅
  │   └── main.py               # FastAPI app ✅
  ├── migrations/               # Database migrations ✅
  └── requirements.txt          # Dependencies ✅
```

### Frontend (KEEP - Essential)
```
frontend/
  ├── app/                      # Next.js pages ✅
  │   ├── dashboard/
  │   ├── dhwani/              # Audio recording
  │   ├── lakshya/             # Lead management
  │   ├── arjun/               # Event discovery
  │   └── login/
  ├── components/               # React components ✅
  ├── lib/                      # Utilities ✅
  └── public/                   # Static assets ✅
```

### Configuration Files (KEEP)
- `.env` ✅ (Gitignored - contains secrets)
- `.gitignore` ✅
- `requirements.txt` ✅ (Main Python deps)
- `agent_requirements.txt` ✅ (CrewAI deps)
- `docker-compose.yml` ✅

### Data Directories (KEEP)
- `leads_data/` ✅ (Generated leads JSON)
- `discovered_events/` ✅ (Event discovery results)
- `recordings/` ✅ (User audio files)
- `transcripts/` ✅ (Generated transcripts)

### Assets (KEEP)
- `lyncsea logo.png` ✅
- `Lyncsea_server.pem` ✅ (EC2 key - secure!)
- `Lyncsea_db_keys.pem` ✅ (DB key - secure!)

---

## 📦 ARCHIVE (Old/Test Files - ZIP & MOVE)

### Development/Test Scripts
- `test_audio_devices.py` → **ARCHIVE**
- `test_recording_simple.py` → **ARCHIVE**
- `process_transcript.py` → **ARCHIVE** (superseded by backend service)
- `record_audio.py` → **ARCHIVE** (superseded by frontend)
- `quick-start.sh` → **ARCHIVE** (old script)

### PDF Generation (Not used in production)
- `convert_to_pdf.py` → **ARCHIVE**
- `generate_pdf.py` → **ARCHIVE**
- `generate_pdf_simple.sh` → **ARCHIVE**
- `pdfs/` directory → **ARCHIVE**

### Example/Template Files
- `user_profile_example.json` → **ARCHIVE** (just an example)

### Old Requirements
- `poc_requirements.txt` → **ARCHIVE** (POC phase over)

### Existing Archive
- `archive/` → **KEEP** (already archived files)

---

## 📝 DOCUMENTATION CLEANUP

### KEEP (1-2 Essential Docs)
- `README.md` ✅ - Update with Lyncsea branding
- `CLAUDE.md` ✅ - Update AYKA → Lyncsea

### ARCHIVE (Too Many Docs - Consolidate)
- `ARCHITECTURE.md` → **ARCHIVE** (outdated?)
- `DEPLOYMENT_PLAN.md` → **ARCHIVE** (duplicate of EC2_DEPLOYMENT_GUIDE)
- `DEPLOYMENT.md` → **ARCHIVE** (just created, incomplete)
- `EC2_DEPLOYMENT_GUIDE.md` → **KEEP** (most relevant)
- `ROADMAP.md` → **ARCHIVE** (outdated features)
- `docs/` → **ARCHIVE** (empty or old)

### Recommendation:
Create ONE file: `DEPLOYMENT.md` (consolidate EC2 + deployment info)
Create ONE file: `README.md` (project overview)
Keep: `CLAUDE.md` (for Claude context)

---

## 🔄 RENAMING TASKS

### Files to Rename
1. `ayka_crew.py` → `lyncsea_crew.py`
2. `ayka_agent.py` → `lyncsea_agent.py` (or archive if duplicate)
3. `ayka_agent.log` → `lyncsea_agent.log`
4. `ayka_event_discovery.log` → `lyncsea_event_discovery.log`

### Code References to Update
1. **backend/app/services/lead_generation.py**
   - Import: `from ayka_crew import AYKACrew` → `from lyncsea_crew import LyncseaCrew`
   - Class usage: `AYKACrew()` → `LyncseaCrew()`

2. **backend/app/core/config.py**
   - `APP_NAME: str = "Ayka Lead Generation"` → `"Lyncsea"`
   - `DATABASE_URL` user: `ayka` → `lyncsea` (?)
   - `AWS_BUCKET_NAME: str = "ayka-recordings"` → `"lyncsea-recordings"`

3. **backend/app/services/event_discovery_agent.py**
   - Logger name: `logger = logging.getLogger('ayka_events')` → `'lyncsea_events'`
   - Log file: `'ayka_event_discovery.log'` → `'lyncsea_event_discovery.log'`

4. **backend/app/models/database.py**
   - Docstring: `SQLAlchemy database models for AYKA platform` → `Lyncsea`

5. **backend/app/agents/conversation_analyzer.py**
   - Prompt: `You are an AI analyst for AYKA lead generation platform` → `Lyncsea`

6. **README.md**
   - All references: AYKA → Lyncsea

7. **CLAUDE.md**
   - Title: `# AYKA Lead Generation - Agent System` → `Lyncsea`

8. **Frontend** (Already has Lyncsea branding mostly)
   - Check for any remaining "AYKA" references

### Database Renaming (⚠️ CAREFUL!)
**Current:** Database name is `ayka`, user is `ayka`
**Options:**
1. **Keep as is** - Database names don't need to match product name
2. **Rename** - `ayka` → `lyncsea` (requires migration, backup first!)

**Recommendation:** Keep database name as `ayka` for now (less risky)

---

## 🗂️ FINAL CLEAN STRUCTURE

```
lyncsea/                          # Renamed from ayka_lead_gen
├── .env                          # Environment variables (gitignored)
├── .gitignore                    # Git ignore rules
├── README.md                     # Main documentation
├── CLAUDE.md                     # Agent system docs
├── DEPLOYMENT.md                 # Deployment guide
├── lyncsea_crew.py               # Lead generation agent
├── event_discovery.py            # Event discovery agent
├── agent_requirements.txt        # Agent dependencies
├── requirements.txt              # Main dependencies
├── docker-compose.yml            # Docker setup
├── lyncsea_agent.log             # Agent logs
├── lyncsea_event_discovery.log   # Event discovery logs
├── Lyncsea_server.pem            # EC2 key
├── Lyncsea_db_keys.pem           # DB key
├── lyncsea logo.png              # Logo asset
│
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── api/                  # API endpoints
│   │   ├── core/                 # Configuration
│   │   ├── models/               # Database models
│   │   ├── services/             # Business logic
│   │   └── main.py
│   ├── migrations/               # SQL migrations
│   └── requirements.txt
│
├── frontend/                     # Next.js frontend
│   ├── app/                      # Pages
│   ├── components/               # Components
│   ├── lib/                      # Utilities
│   └── public/                   # Static files
│
├── leads_data/                   # Generated leads
├── discovered_events/            # Event discoveries
├── recordings/                   # Audio files
├── transcripts/                  # Transcripts
│
└── archive_old/                  # Zipped old files
    └── development_files_2025_11_15.zip
```

---

## ✅ ACTION CHECKLIST

### Phase 1: Archive Old Files
- [ ] Create `archive_old/` directory
- [ ] Move test files to archive
- [ ] Move PDF generation files to archive
- [ ] Move old docs to archive
- [ ] Zip archive: `development_files_2025_11_15.zip`
- [ ] Delete originals after confirming zip

### Phase 2: Rename Files
- [ ] `ayka_crew.py` → `lyncsea_crew.py`
- [ ] `ayka_agent.py` → decide: rename or archive?
- [ ] Log files → lyncsea_*.log

### Phase 3: Update Code References
- [ ] Update imports in `lead_generation.py`
- [ ] Update class names: `AYKACrew` → `LyncseaCrew`
- [ ] Update config.py (APP_NAME, etc.)
- [ ] Update event_discovery_agent.py (logger, log file)
- [ ] Update database.py (docstrings)
- [ ] Update conversation_analyzer.py (prompts)

### Phase 4: Update Documentation
- [ ] README.md (AYKA → Lyncsea)
- [ ] CLAUDE.md (AYKA → Lyncsea)
- [ ] Consolidate deployment docs into one DEPLOYMENT.md
- [ ] Archive old docs

### Phase 5: Test
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Lead generation works
- [ ] Event discovery works
- [ ] Database connections work

### Phase 6: Git Commit
- [ ] `git add .`
- [ ] `git commit -m "Rebrand from AYKA to Lyncsea, cleanup codebase"`
- [ ] `git push`

---

## 🚨 RISKS & CONSIDERATIONS

1. **Database Naming**
   - Current DB: `ayka` user, `ayka` database
   - **Recommendation:** Keep as-is to avoid migration issues
   - If renaming: Backup first, test locally

2. **Import Breakage**
   - Renaming `ayka_crew.py` will break imports
   - Must update ALL files that import it

3. **Log Files**
   - Old log files have valuable history
   - Keep old logs, new logs use new names

4. **EC2 Deployment**
   - File renames need to be reflected on server
   - Update systemd service files if they reference old names

5. **Environment Variables**
   - Check if any .env variables reference "ayka"
   - Update if needed

---

## 📊 FILE COUNT SUMMARY

**Current Total:** ~47 files/folders in root
**After Cleanup:** ~25 files/folders
**Space Saved:** ~15-20 files archived

---

## 🎯 NEXT STEPS

1. **Review this plan** - Make sure we agree on what to keep/archive
2. **Backup everything** - `git commit` current state before changes
3. **Execute Phase 1** - Archive old files
4. **Execute Phase 2-3** - Rename & update code
5. **Test locally** - Make sure everything works
6. **Update EC2** - Deploy to production

**Estimated Time:** 2-3 hours for full cleanup & testing