# AYKA Lead Generation Platform - Roadmap

## Current State (Working POC)

✅ **Audio Recording** - Real-time transcription with speaker detection
✅ **Lead Generation Agent** - Analyzes transcripts, extracts leads, sends emails
✅ **Event Discovery Agent** - Finds relevant events based on user profile
✅ **Multi-Agent System** - CrewAI with 4+ specialized agents
✅ **Email Notifications** - HTML formatted emails with insights

---

## Phase 1: Production Ready Backend (2-3 weeks)

### 1.1 API Layer
- [ ] FastAPI REST endpoints
  - `POST /recordings/upload` - Upload audio files
  - `POST /recordings/process` - Process existing recordings
  - `GET /leads` - Fetch extracted leads
  - `POST /events/discover` - Trigger event discovery
  - `GET /users/{id}/profile` - User profile management

### 1.2 Database Integration
- [ ] PostgreSQL for structured data (users, recordings, leads)
- [ ] Redis for job queue and caching
- [ ] File storage (S3/local) for audio files

### 1.3 Background Processing
- [ ] Celery workers for async transcription
- [ ] Agent execution as background jobs
- [ ] Webhook notifications when processing completes

### 1.4 Authentication & Multi-tenancy
- [ ] JWT authentication
- [ ] User management
- [ ] Organization/team support

---

## Phase 2: Web Application (3-4 weeks)

### 2.1 Frontend Tech Stack
**Recommended**: Next.js + TypeScript + Tailwind CSS

### 2.2 Core Pages
- [ ] **Dashboard** - Overview of recordings, leads, events
- [ ] **Recordings** - Upload, manage, view transcripts
- [ ] **Leads** - Browse leads with filters, export to CRM
- [ ] **Events** - Discovered events calendar view
- [ ] **Profile** - User preferences for event discovery
- [ ] **Settings** - Email notifications, integrations

### 2.3 Key Features
- [ ] Drag-drop audio upload
- [ ] Real-time processing status
- [ ] Lead cards with contact info, LinkedIn links
- [ ] Event recommendations with registration CTAs
- [ ] Search and filter across all data

---

## Phase 3: Advanced Features (4-6 weeks)

### 3.1 Real-time Recording
- [ ] Browser-based audio recording
- [ ] Mobile app for on-the-go recording
- [ ] Live transcription display

### 3.2 CRM Integration
- [ ] Salesforce connector
- [ ] HubSpot integration
- [ ] Export to CSV/Excel
- [ ] Zapier webhooks

### 3.3 Smart Matching
- [ ] Neo4j graph for interest matching
- [ ] "People you should meet" recommendations
- [ ] Connection strength scoring

### 3.4 Analytics
- [ ] Networking insights dashboard
- [ ] Event ROI tracking
- [ ] Lead conversion metrics

---

## Phase 4: Scale & Polish (Ongoing)

### 4.1 Performance
- [ ] Batch processing for multiple recordings
- [ ] Caching for faster agent responses
- [ ] Optimize Whisper model selection

### 4.2 AI Improvements
- [ ] Fine-tune prompts based on user feedback
- [ ] Custom event preferences learning
- [ ] Better speaker identification

### 4.3 Deployment
- [ ] Docker containers for all services
- [ ] CI/CD pipeline
- [ ] Production monitoring (Sentry, DataDog)
- [ ] Auto-scaling for workers

---

## Updated Plan: Mobile + Web with Click-to-Record

### Mobile & Web Features
- **Web**: Browser audio recording API (no file upload)
- **Mobile**: Native audio recording (React Native)
- **Flow**: Click record → auto process → show results
- **Architecture**: Modular FastAPI backend with feature flags

See `DEPLOYMENT_PLAN.md` for complete infrastructure details.

---

## Recommended Next Steps (Priority Order)

### Immediate (This Week)
1. **Create FastAPI backend**
   - Basic endpoints for upload and process
   - Connect to SQLite for now (easy migration to PostgreSQL later)
   - Test with existing Python scripts

2. **Simple Web UI**
   - Single page app with file upload
   - Display processing status
   - Show results (leads + events)

### Next Week
3. **User Authentication**
   - Simple email/password login
   - Session management
   - User-specific data isolation

4. **Background Jobs**
   - Celery setup for async processing
   - Job status tracking
   - Email notifications on completion

### Week 3-4
5. **Full Dashboard**
   - Next.js frontend with proper routing
   - All CRUD operations
   - Export functionality

6. **Deploy MVP**
   - Docker Compose for easy deployment
   - Deploy to VPS or cloud
   - Beta testing with real users

---

## Tech Stack Recommendation

### Backend
- **Framework**: FastAPI (already in your docker-compose)
- **Database**: PostgreSQL + Redis
- **Queue**: Celery
- **Storage**: S3 or local filesystem
- **AI**: OpenAI GPT-4 (current) + CrewAI

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + shadcn/ui
- **State**: React Query for API calls
- **Auth**: NextAuth.js

### DevOps
- **Containers**: Docker + Docker Compose
- **Deployment**: AWS/GCP/DigitalOcean
- **Monitoring**: Sentry + LogRocket
- **Analytics**: PostHog or Mixpanel

---

## MVP Scope (4 weeks)

**Goal**: Functional web app for 10-50 beta users

### Must Have
1. User signup/login
2. Upload audio recordings via web
3. View transcripts with speaker labels
4. Browse extracted leads with contact info
5. See recommended events
6. Export leads to CSV

### Nice to Have
- Real-time recording from browser
- CRM integration
- Advanced search/filters
- Mobile responsive design

### Not in MVP
- Mobile app
- Graph database matching
- Custom AI model fine-tuning
- Team collaboration features

---

## Success Metrics

### Technical
- Audio processing time < 2 minutes for 30-min recording
- Agent processing time < 1 minute per transcript
- 95%+ uptime
- Support 100+ concurrent users

### Business
- 80%+ accuracy in lead extraction
- 90%+ event relevance score from users
- 50%+ of leads contacted within 7 days
- 30%+ conversion from free to paid (if monetizing)

---

## Questions to Decide

1. **Monetization**: Free tier vs. paid plans?
2. **Target Users**: Individual professionals or enterprise teams?
3. **Data Privacy**: How to handle sensitive conversation data?
4. **Hosting**: Self-hosted or cloud SaaS?
5. **Mobile**: Web-first or mobile app needed?

---

## Conclusion

**Recommended Path**:
1. Build FastAPI backend with minimal DB (Week 1-2)
2. Create simple Next.js frontend (Week 2-3)
3. Deploy MVP and get feedback (Week 4)
4. Iterate based on user needs

You have solid AI agents. Focus on making them accessible via a clean web interface.