# AYKA Platform - Deployment & Architecture Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT APPS                          │
├──────────────────────┬──────────────────────────────────┤
│   Web (Next.js)      │   Mobile (React Native)          │
│   - Record audio     │   - Record audio                 │
│   - View leads       │   - View leads                   │
│   - Browse events    │   - Browse events                │
└──────────┬───────────┴──────────────┬───────────────────┘
           │                          │
           └──────────────┬───────────┘
                          │ HTTPS
                          ▼
           ┌──────────────────────────┐
           │   AWS API Gateway         │
           │   (Load Balancer)         │
           └──────────┬────────────────┘
                      │
           ┌──────────┴────────────┐
           │                       │
           ▼                       ▼
   ┌──────────────┐        ┌──────────────┐
   │  FastAPI     │        │  FastAPI     │
   │  Instance 1  │        │  Instance 2  │
   │  (EC2)       │        │  (EC2)       │
   └──────┬───────┘        └──────┬───────┘
          │                       │
          └───────────┬───────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
   ┌──────────────┐        ┌──────────────┐
   │  PostgreSQL  │        │   Redis      │
   │  (RDS)       │        │  (ElastiCache)│
   └──────────────┘        └──────────────┘
          │
          ▼
   ┌──────────────┐
   │   S3         │
   │  Audio Files │
   └──────────────┘
          │
          ▼
   ┌──────────────────────┐
   │  E2E GPU Instance    │
   │  - Whisper (STT)     │
   │  - Speaker Detection │
   │  - Agent Processing  │
   └──────────────────────┘
```

---

## Deployment Architecture

### 1. **Frontend (Web + Mobile)**
**Location**: Vercel (Web) + App Stores (Mobile)

#### Web App (Next.js)
- **Hosting**: Vercel (free tier → $20/month pro)
- **CDN**: Built-in with Vercel
- **Features**:
  - Click record → browser audio API
  - Upload to S3 via presigned URLs
  - Real-time status via WebSocket

#### Mobile App (React Native)
- **Framework**: Expo/React Native
- **Features**:
  - Native audio recording
  - Push notifications
  - Offline queue for recordings
- **Distribution**: TestFlight (iOS) + Google Play Internal Testing

---

### 2. **Backend API (FastAPI)**
**Location**: AWS EC2

#### Configuration
- **Instance**: t3.medium (2 vCPU, 4GB RAM) × 2
- **OS**: Ubuntu 22.04
- **Web Server**: Uvicorn + Nginx reverse proxy
- **Load Balancer**: AWS Application Load Balancer
- **Auto Scaling**: Based on CPU/memory usage

#### Services
```
EC2 Instance 1 & 2:
├── FastAPI (Port 8000)
│   ├── /api/auth/*
│   ├── /api/recordings/*
│   ├── /api/leads/*
│   ├── /api/events/*
│   └── /api/users/*
├── Celery Workers (Background tasks)
└── Nginx (Reverse proxy)
```

**Estimated Cost**: $60-80/month (2 instances + load balancer)

---

### 3. **AI Processing (GPU Instance)**
**Location**: E2E Cloud GPU / AWS EC2 GPU

#### Option A: E2E Cloud (Recommended for cost)
- **Instance**: 1× NVIDIA T4 (16GB VRAM)
- **Specs**: 4 vCPU, 16GB RAM, 1TB SSD
- **Cost**: ₹15,000-20,000/month (~$180-240)

#### What Runs Here
```
GPU Instance:
├── Whisper Model (base/medium)
│   └── Transcription processing
├── Pyannote (Speaker Diarization)
│   └── Speaker identification
├── CrewAI Agents
│   ├── Lead Generation Agent
│   ├── Event Discovery Agent
│   └── Email Agent
└── Job Queue Consumer (Celery)
```

#### Communication
- **Queue**: Redis on EC2 → GPU pulls jobs
- **Storage**: Reads audio from S3, writes results to PostgreSQL
- **Network**: VPC peering between AWS and E2E (or VPN)

---

### 4. **Database Layer**

#### PostgreSQL (Primary Database)
- **Hosting**: AWS RDS
- **Instance**: db.t3.micro (1 vCPU, 1GB) to start
- **Storage**: 20GB SSD
- **Backup**: Automated daily snapshots
- **Cost**: ~$15-25/month

**Schema**:
```sql
users, recordings, transcripts, leads,
events, user_profiles, notifications
```

#### Redis (Cache + Queue)
- **Hosting**: AWS ElastiCache
- **Instance**: cache.t3.micro
- **Use Cases**:
  - Session storage
  - Celery job queue
  - API response caching
- **Cost**: ~$15/month

---

### 5. **Storage (S3)**
**Location**: AWS S3

#### Buckets
- `ayka-recordings-prod` - Audio files
- `ayka-static-assets` - Images, exports

**Configuration**:
- Presigned URLs for direct client upload
- Lifecycle policy: Archive to Glacier after 90 days
- Encryption at rest

**Cost**: ~$5-10/month (100GB storage)

---

## Deployment Workflow

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-api:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Build Docker image
      - Push to ECR
      - Deploy to EC2 via SSH
      - Run migrations
      - Restart services

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Build Next.js app
      - Deploy to Vercel (auto)
```

---

## Modular Architecture

### Backend Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py          # Authentication
│   │   ├── recordings.py    # Upload, process
│   │   ├── leads.py         # CRUD for leads
│   │   ├── events.py        # Event discovery
│   │   └── users.py         # User management
│   ├── agents/
│   │   ├── lead_agent.py    # Lead generation
│   │   ├── event_agent.py   # Event discovery
│   │   └── email_agent.py   # Email sending
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # JWT, hashing
│   │   └── db.py            # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── workers/             # Celery tasks
├── tests/
└── requirements.txt
```

### Frontend Structure
```
frontend/
├── app/                     # Next.js app router
│   ├── (auth)/
│   │   ├── login/
│   │   └── signup/
│   ├── dashboard/
│   ├── recordings/
│   ├── leads/
│   └── events/
├── components/
│   ├── ui/                  # Reusable components
│   ├── RecordButton.tsx     # Audio recording
│   ├── LeadCard.tsx
│   └── EventCard.tsx
├── lib/
│   ├── api.ts              # API client
│   └── utils.ts
└── public/
```

### Mobile Structure
```
mobile/
├── src/
│   ├── screens/
│   │   ├── RecordScreen.tsx
│   │   ├── LeadsScreen.tsx
│   │   └── EventsScreen.tsx
│   ├── components/
│   ├── navigation/
│   └── services/
│       └── audio.ts         # Native recording
└── app.json
```

---

## Cost Breakdown (Monthly)

| Service                | Provider      | Cost (USD) |
|------------------------|---------------|------------|
| Web Hosting            | Vercel        | $0-20      |
| Mobile (Dev)           | Free          | $0         |
| API Servers (2×)       | AWS EC2       | $60-80     |
| GPU Instance           | E2E Cloud     | $180-240   |
| PostgreSQL             | AWS RDS       | $15-25     |
| Redis                  | ElastiCache   | $15        |
| S3 Storage             | AWS S3        | $5-10      |
| Load Balancer          | AWS ALB       | $20        |
| Monitoring             | Sentry        | $0-26      |
| **Total**              |               | **$295-416/month** |

**With E2E GPU discount**: ~₹25,000-30,000/month (~$300-360)

---

## Scaling Strategy

### Phase 1: MVP (0-100 users)
- Single EC2 API instance
- Single GPU instance
- RDS micro instance
- **Cost**: ~$250/month

### Phase 2: Growth (100-1000 users)
- 2× API instances with load balancer
- Keep single GPU (batch processing)
- Upgrade RDS to small
- **Cost**: ~$400/month

### Phase 3: Scale (1000+ users)
- Auto-scaling API instances (2-5)
- 2× GPU instances
- RDS medium with read replicas
- Add CDN for static assets
- **Cost**: ~$800-1200/month

---

## Implementation Plan

### Week 1: Infrastructure Setup
- [ ] Provision AWS resources (EC2, RDS, S3)
- [ ] Setup E2E GPU instance
- [ ] Configure VPC, security groups
- [ ] Install Docker on all instances

### Week 2: Backend API
- [ ] FastAPI project structure
- [ ] Database models and migrations
- [ ] Auth endpoints (JWT)
- [ ] Recording upload endpoint
- [ ] Celery setup for async tasks

### Week 3: Frontend (Web)
- [ ] Next.js project with Tailwind
- [ ] Audio recording component
- [ ] Upload to S3 with progress
- [ ] Dashboard with recordings list
- [ ] Leads and events display

### Week 4: Integration & Testing
- [ ] Connect frontend to API
- [ ] GPU processing pipeline
- [ ] End-to-end testing
- [ ] Deploy to staging

### Week 5: Mobile App
- [ ] React Native setup
- [ ] Native audio recording
- [ ] API integration
- [ ] TestFlight/Internal testing

### Week 6: Production Launch
- [ ] CI/CD pipeline
- [ ] Monitoring setup
- [ ] SSL certificates
- [ ] Beta user onboarding

---

## Security Checklist

- [ ] HTTPS everywhere (SSL certificates)
- [ ] JWT authentication with refresh tokens
- [ ] Rate limiting on API endpoints
- [ ] S3 bucket policies (no public access)
- [ ] RDS encryption at rest
- [ ] Secrets in AWS Secrets Manager
- [ ] Regular security audits
- [ ] GDPR compliance for EU users

---

## Monitoring & Alerts

### Tools
- **Application**: Sentry (errors)
- **Infrastructure**: AWS CloudWatch
- **Logs**: CloudWatch Logs or Loki
- **Uptime**: UptimeRobot (free)

### Key Metrics
- API response time < 500ms
- GPU processing queue length
- Database connection pool
- S3 upload success rate
- Agent success rate

---

## Backup Strategy

- **Database**: RDS automated daily backups (7-day retention)
- **Audio Files**: S3 versioning enabled
- **Code**: Git + GitHub (private repo)
- **Secrets**: AWS Secrets Manager backup

---

## Next Immediate Steps

1. **Setup AWS Account** (if not already)
2. **Provision E2E GPU instance**
3. **Create project structure** (backend + frontend)
4. **Dockerize everything** for easy deployment
5. **Build MVP API** (auth + upload + process)
6. **Build recording UI** (web first, then mobile)

---

## Questions?

Ready to start building? I can help you:
1. Set up the FastAPI backend structure
2. Create the Next.js frontend with recording
3. Write deployment scripts
4. Configure Docker containers

What do you want to tackle first?