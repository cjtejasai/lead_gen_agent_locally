# Ayka Lead Generation Platform - Architecture

## Overview
A platform that processes audio/video data from wearable devices at events to identify collaboration opportunities using LLMs and graph-based interest matching.

## System Architecture

```
┌─────────────────┐
│  Wearable Device│  (Pendant/Locket - Hardware)
│  Audio/Video    │
└────────┬────────┘
         │ Upload
         ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend Platform                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │         1. Data Ingestion API (FastAPI)          │  │
│  │    - Receive audio/video from pendant            │  │
│  │    - Queue processing jobs                       │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │      2. Speech-to-Text Processing Pipeline       │  │
│  │    - Whisper API / AssemblyAI                    │  │
│  │    - Extract transcripts with timestamps         │  │
│  │    - Speaker diarization                         │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │      3. LLM-based Agentic Analysis System        │  │
│  │    Agent 1: Content Analyzer                     │  │
│  │      - Extract topics, interests, pain points    │  │
│  │      - Identify business needs/offerings         │  │
│  │                                                   │  │
│  │    Agent 2: Entity Extractor                     │  │
│  │      - Extract person names, companies           │  │
│  │      - Categorize user type (CEO/Student/Other)  │  │
│  │                                                   │  │
│  │    Agent 3: Intent Classifier                    │  │
│  │      - Looking for: investment, partnership,     │  │
│  │        collaboration, hiring, learning, etc.     │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │      4. Graph Database (Neo4j)                   │  │
│  │    Nodes:                                        │  │
│  │      - Person (name, category, contact)          │  │
│  │      - Interest (topic, domain)                  │  │
│  │      - Event (name, date, location)              │  │
│  │      - Company (name, industry)                  │  │
│  │      - Need (type, description)                  │  │
│  │      - Offering (type, description)              │  │
│  │                                                   │  │
│  │    Relationships:                                │  │
│  │      - INTERESTED_IN                             │  │
│  │      - WORKS_AT                                  │  │
│  │      - ATTENDED                                  │  │
│  │      - LOOKING_FOR                               │  │
│  │      - OFFERS                                    │  │
│  │      - MATCHED_WITH (score, reason)              │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │      5. Matching & Lead Generation Engine        │  │
│  │    - Graph traversal algorithms                  │  │
│  │    - Semantic similarity (embeddings)            │  │
│  │    - LLM-based match scoring                     │  │
│  │    - Generate collaboration suggestions          │  │
│  └──────────────┬───────────────────────────────────┘  │
│                 │                                        │
│                 ▼                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │      6. Calendar Integration & Scheduling        │  │
│  │    - Generate meeting links                      │  │
│  │    - Calendar invites (Google/Outlook)           │  │
│  │    - Follow-up reminders                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│           Frontend (Next.js + Modern UI)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Dashboard                                       │  │
│  │    - Upload pendant recordings                   │  │
│  │    - View processing status                      │  │
│  │    - Match recommendations feed                  │  │
│  │    - Interest graph visualization                │  │
│  │    - Lead pipeline (kanban view)                 │  │
│  │    - Calendar integration                        │  │
│  │    - Analytics & insights                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## User Categories

### 1. CEO / Investor
- **Looking for:** Investment opportunities, partnerships, acquisitions, strategic connections
- **Offers:** Funding, mentorship, network access, business development

### 2. Students
- **Looking for:** Internships, learning opportunities, mentorship, career guidance, projects
- **Offers:** Fresh perspectives, technical skills, enthusiasm, research capabilities

### 3. General / Other
- **Looking for:** Various (collaborations, partnerships, hiring, services, etc.)
- **Offers:** Various (expertise, services, products, connections, etc.)

## Data Flow

1. **Recording Phase**
   - User wears pendant at event
   - Device continuously records audio (with user consent)
   - Recording stored locally with timestamps

2. **Upload Phase**
   - User uploads recording via mobile app or web dashboard
   - Files stored in cloud storage (S3/GCS)
   - Processing job queued

3. **Processing Phase**
   - Speech-to-text conversion
   - Speaker diarization (identify different speakers)
   - Transcript generated with timestamps

4. **Analysis Phase**
   - LLM agents analyze transcript:
     - Extract key topics and interests
     - Identify pain points and needs
     - Extract offerings and capabilities
     - Categorize user intent
     - Extract entities (people, companies)

5. **Graph Population**
   - Create/update nodes in Neo4j
   - Establish relationships based on analysis
   - Store embeddings for semantic search

6. **Matching Phase**
   - Run matching algorithms
   - Find complementary needs/offerings
   - Score matches using LLM
   - Generate collaboration suggestions

7. **Lead Generation**
   - Present matches in dashboard
   - Provide context and reasoning
   - Enable one-click calendar scheduling
   - Track lead status and follow-ups

## Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **Task Queue:** Celery + Redis
- **Database:** Neo4j (graph) + PostgreSQL (relational)
- **Storage:** AWS S3 / Google Cloud Storage
- **Speech-to-Text:** OpenAI Whisper API / AssemblyAI
- **LLM:** OpenAI GPT-4 / Anthropic Claude
- **Embeddings:** OpenAI text-embedding-3

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **UI Library:** shadcn/ui + Tailwind CSS
- **State Management:** Zustand / React Query
- **Visualization:** D3.js / Recharts for graphs
- **Calendar:** Cal.com API integration

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose (dev) / Kubernetes (prod)
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry + Prometheus + Grafana

## Security & Privacy Considerations

1. **Consent Management**
   - Users must explicitly consent to recording
   - Event-level and conversation-level consent tracking

2. **Data Encryption**
   - At-rest: AES-256 encryption
   - In-transit: TLS 1.3

3. **Access Control**
   - Role-based access control (RBAC)
   - Users can only see their own recordings and matches

4. **Data Retention**
   - Configurable retention policies
   - Right to be forgotten (GDPR compliance)

5. **PII Protection**
   - Automatic detection and redaction of sensitive info
   - Anonymization options

## Scalability Considerations

1. **Async Processing**
   - All heavy processing (STT, LLM) done asynchronously
   - Job queue with retry mechanisms

2. **Caching**
   - Redis for API response caching
   - Embedding cache for repeat queries

3. **Rate Limiting**
   - API rate limits per user/tier
   - LLM usage quotas

4. **Database Optimization**
   - Neo4j indexes on frequently queried properties
   - PostgreSQL connection pooling

## Future Enhancements

1. Real-time processing during events
2. Mobile app for pendant management
3. Multi-language support
4. Video analysis (facial recognition, object detection)
5. Integration with CRM systems (Salesforce, HubSpot)
6. AI-generated follow-up emails
7. Sentiment analysis
8. Industry-specific matching algorithms
