# 🚀 Lyncsea - Hiring & Scaling Plan

## 📊 Current State Analysis

**Codebase Size:** ~10,500 lines of code
**Tech Stack:**
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: FastAPI (Python), PostgreSQL, Neo4j (ready but not deployed)
- AI/ML: LangChain, OpenAI GPT-4, AssemblyAI, Pyannote
- Infrastructure: AWS (EC2, S3), Screen sessions (manual deployment)

**Key Features:**
- ✅ Audio recording (Dhwani)
- ✅ AI transcription (AssemblyAI)
- ✅ Lead generation (AI agents)
- ✅ Action items extraction (Karya)
- ✅ Speaker diarization
- ✅ Dashboard with real-time stats
- ⏳ Neo4j graph database (designed but not integrated)
- ⏳ Event discovery

---

## 👥 HIRING PLAN BY GROWTH STAGE

### **Phase 1: MVP to 100 Users (0-3 months) - BOOTSTRAP**

**Team Size: 2-3 people (Part-time or Full-time founders)**

| Role | FTE | Duration | Monthly Cost (India) | Responsibilities |
|------|-----|----------|---------------------|------------------|
| **Full-Stack Developer** | 1.0 | Full-time | ₹80k-₹1.2L ($1k-$1.5k) | Bug fixes, UI polish, feature completion |
| **AI/ML Engineer** (You?) | 0.5 | Part-time | ₹40k-₹60k ($500-$750) | Agent optimization, prompt engineering |
| **DevOps** (Contractor) | 0.2 | As-needed | ₹20k ($250) | CI/CD setup, move from screen to Docker |

**Total Monthly: ₹1.4L - ₹2L ($1,750 - $2,500)**

**What to Build:**
- Fix audio recording bugs across all browsers
- Complete Neo4j integration for better matching
- Add email notifications for action items
- Set up proper CI/CD (GitHub Actions + AWS ECS/Fargate)
- Add monitoring (Sentry, Datadog)

---

### **Phase 2: 100-1,000 Users (3-9 months) - PRODUCT-MARKET FIT**

**Team Size: 5-7 people**

| Role | FTE | Duration | Monthly Cost (India) | Skills Required |
|------|-----|----------|---------------------|-----------------|
| **Frontend Engineer** | 1.0 | Full-time | ₹1.2L-₹1.8L ($1.5k-$2.2k) | Next.js, React, TypeScript, Framer Motion, Tailwind |
| **Backend Engineer** | 1.0 | Full-time | ₹1.2L-₹1.8L ($1.5k-$2.2k) | FastAPI, PostgreSQL, Redis, REST APIs |
| **AI/ML Engineer** | 1.0 | Full-time | ₹1.5L-₹2.5L ($1.8k-$3k) | LangChain, OpenAI, Prompt Engineering, RAG |
| **Data Scientist** | 0.5 | Part-time | ₹75k-₹1L ($900-$1.2k) | Neo4j, Graph algorithms, Matching algorithms |
| **DevOps Engineer** | 0.5 | Part-time | ₹60k-₹80k ($750-$1k) | AWS, Docker, Kubernetes, Terraform |
| **QA/Testing** | 0.5 | Part-time | ₹40k-₹60k ($500-$750) | Manual + Automated testing, Playwright |
| **Product Manager** | 0.5 | Part-time | ₹80k-₹1.2L ($1k-$1.5k) | User research, Feature prioritization |

**Total Monthly: ₹6L - ₹9.5L ($7,500 - $12,000)**

**Infrastructure Costs (Monthly):**
- AWS (EC2, RDS, S3, CloudFront): $500-$1,000
- AssemblyAI API (1k hours/month): $250-$500
- OpenAI API (GPT-4): $500-$1,500
- Neo4j Aura (managed): $200-$400
- Sentry, Datadog: $100-$200
- **Total Infra: $1,550 - $3,600**

**What to Build:**
- Mobile app (React Native)
- Advanced matching algorithms (Graph ML)
- Integration with LinkedIn, Google Calendar
- Analytics dashboard for users
- White-label solution for enterprises

---

### **Phase 3: 1,000-10,000 Users (9-18 months) - SCALE**

**Team Size: 12-15 people**

| Role | FTE | Monthly Cost (India) | Skills Required |
|------|-----|---------------------|-----------------|
| **Senior Frontend Engineer** | 1.0 | ₹2L-₹3L ($2.5k-$3.7k) | Next.js, Performance optimization, SSR/ISR |
| **Junior Frontend Engineer** | 1.0 | ₹80k-₹1.2L ($1k-$1.5k) | React, TypeScript, UI components |
| **Senior Backend Engineer** | 1.0 | ₹2L-₹3L ($2.5k-$3.7k) | FastAPI, Microservices, Async processing |
| **Backend Engineer** | 2.0 | ₹2.4L-₹3.6L ($3k-$4.5k) | APIs, Database optimization |
| **AI/ML Lead** | 1.0 | ₹3L-₹5L ($3.7k-$6.2k) | Fine-tuning LLMs, Agent orchestration |
| **ML Engineer** | 1.0 | ₹1.5L-₹2.5L ($1.8k-$3k) | Model training, RAG pipelines |
| **Data Scientist** | 1.0 | ₹1.5L-₹2.5L ($1.8k-$3k) | Graph analytics, Recommendation systems |
| **DevOps Lead** | 1.0 | ₹2L-₹3L ($2.5k-$3.7k) | Kubernetes, Multi-region deployment |
| **DevOps Engineer** | 1.0 | ₹1.2L-₹1.8L ($1.5k-$2.2k) | CI/CD, Monitoring, Security |
| **QA Lead** | 1.0 | ₹1.5L-₹2L ($1.8k-$2.5k) | Test automation, Performance testing |
| **Product Manager** | 1.0 | ₹2L-₹3L ($2.5k-$3.7k) | Roadmap, Stakeholder management |
| **UI/UX Designer** | 1.0 | ₹1.2L-₹2L ($1.5k-$2.5k) | Figma, User research, A/B testing |
| **Technical Writer** | 0.5 | ₹50k-₹80k ($625-$1k) | API docs, User guides |

**Total Monthly: ₹21L - ₹33L ($26,000 - $41,000)**

**Infrastructure Costs (Monthly):**
- AWS (Multi-region, Auto-scaling): $3,000-$6,000
- AssemblyAI API (10k hours/month): $2,500-$4,000
- OpenAI API (GPT-4 + Fine-tuned models): $3,000-$8,000
- Neo4j Enterprise: $1,000-$2,000
- CDN (CloudFront/Cloudflare): $500-$1,000
- Monitoring & Security: $500-$1,000
- **Total Infra: $10,500 - $22,000**

**What to Build:**
- Real-time collaboration features
- Multi-language support
- Advanced analytics and reporting
- Enterprise SSO/SAML
- API marketplace for integrations
- Fine-tuned models for your domain

---

## 💰 REVENUE vs. COST BREAKDOWN

### **Pricing Model Recommendation:**

| Tier | Monthly Price | Target Users | Features |
|------|--------------|--------------|----------|
| **Free** | $0 | Unlimited | 5 recordings/month, Basic transcription |
| **Pro** | $29/month | 1,000-5,000 | 100 recordings/month, AI insights, Karya |
| **Business** | $99/month | 500-2,000 | Unlimited recordings, Graph matching, Priority support |
| **Enterprise** | $499+/month | 50-200 | Custom deployment, SSO, API access |

### **Cost per User Projections:**

| User Count | Infrastructure Cost/User | Team Cost/User | Total Cost/User | Recommended Revenue/User |
|------------|-------------------------|----------------|-----------------|------------------------|
| **100** | $15-$36 | $75-$250 | $90-$286 | **$50-$100** ⚠️ (Loss) |
| **1,000** | $1.50-$3.60 | $7.50-$12 | $9-$15.60 | **$20-$40** ✅ |
| **10,000** | $1.05-$2.20 | $2.60-$4.10 | $3.65-$6.30 | **$10-$25** ✅ |
| **50,000** | $0.50-$1.20 | $1-$2 | $1.50-$3.20 | **$5-$15** ✅✅ |

**Key Insight:** You'll be **cash-flow negative** until ~500-1,000 users. Need runway or revenue diversification.

---

## 🗄️ WHEN TO USE NEO4J GRAPH DATABASE

### **Use Neo4j When:**

✅ **Now (100+ users)** - Your core value prop is **matching people based on relationships**

**Why?**
1. **Your schema is already designed** (`backend/app/core/neo4j_schema.py`)
2. **Complex matching queries** - Finding common interests, complementary needs/offerings
3. **Better than SQL for:**
   - "Find people who share 3+ interests with me AND need what I offer"
   - "Who are 2nd-degree connections through common interests?"
   - "Shortest path between two people in the network"
4. **Performance:** PostgreSQL JOIN hell vs. Neo4j graph traversal (10-100x faster for relationship queries)

### **PostgreSQL vs. Neo4j Split:**

| Data Type | Database | Reason |
|-----------|----------|--------|
| Users, Auth, Sessions | **PostgreSQL** | ACID, well-understood, mature |
| Recordings, Transcripts | **PostgreSQL** | Append-only, large blobs (S3 ref) |
| Action Items (Karya) | **PostgreSQL** | Simple CRUD, time-series |
| **Interests, Needs, Offerings** | **Neo4j** | Relationship-heavy, matching logic |
| **Person-to-Person Matches** | **Neo4j** | Graph traversal, recommendations |
| **Common Interest Detection** | **Neo4j** | Multi-hop queries |

### **Implementation Priority:**

**Phase 1 (Now - 100 users):**
```
✅ Keep PostgreSQL for operational data
✅ Deploy Neo4j Aura (managed, $200/month free tier)
✅ Dual-write: Save leads to both PostgreSQL + Neo4j
✅ Use Neo4j ONLY for matching/recommendations API
```

**Phase 2 (1,000 users):**
```
✅ Add Graph Data Science (GDS) library for ML-based matching
✅ Implement community detection (find clusters of similar people)
✅ Use PageRank to identify "influencers" in your network
```

**Phase 3 (10,000+ users):**
```
✅ Neo4j Enterprise with multi-region replication
✅ Real-time graph updates with Kafka
✅ Advanced graph algorithms (Link Prediction, Node Similarity)
```

---

## 🛠️ REQUIRED SKILLS BY ROLE

### **1. Frontend Engineer**

**Must-Have:**
- Next.js 14+ (App Router, Server Components, RSC)
- TypeScript (advanced types, generics)
- React Hooks, Context API, State management
- Tailwind CSS, Framer Motion (animations)
- REST API integration, async/await
- Responsive design, PWA

**Nice-to-Have:**
- WebRTC (for real-time audio)
- Web Audio API
- React Query/SWR
- Storybook
- Accessibility (WCAG 2.1)

**Interview Test:**
- Build a real-time chat component with optimistic updates
- Implement infinite scroll with virtualization
- Debug a performance issue (bundle size, re-renders)

---

### **2. Backend Engineer**

**Must-Have:**
- Python 3.10+ (type hints, async/await)
- FastAPI (dependency injection, background tasks)
- PostgreSQL (complex queries, CTEs, window functions)
- SQLAlchemy ORM
- Redis (caching, rate limiting)
- REST API design (versioning, pagination)
- JWT authentication, RBAC
- S3/Blob storage

**Nice-to-Have:**
- Neo4j/Cypher queries
- GraphQL
- Celery/RQ for task queues
- Elasticsearch
- gRPC

**Interview Test:**
- Design an API for a social network (rate limiting, pagination, caching)
- Optimize a slow database query
- Write a middleware for request logging

---

### **3. DevOps Engineer**

**Must-Have:**
- Docker (multi-stage builds, compose)
- Kubernetes (deployments, services, ingress)
- AWS (EC2, ECS, RDS, S3, CloudFront, Lambda)
- Terraform/CloudFormation (IaC)
- CI/CD (GitHub Actions, GitLab CI)
- Nginx/Traefik (reverse proxy)
- Monitoring (Prometheus, Grafana, Datadog)
- Logging (ELK stack, CloudWatch)

**Nice-to-Have:**
- ArgoCD (GitOps)
- Service mesh (Istio)
- Chaos engineering (Chaos Monkey)
- Security scanning (Trivy, Snyk)

**Interview Test:**
- Set up a zero-downtime deployment pipeline
- Debug a production outage (CPU spike, OOM)
- Write a Terraform module for multi-region RDS

---

### **4. AI/ML Engineer**

**Must-Have:**
- LangChain/LlamaIndex (RAG, agents, chains)
- OpenAI API (GPT-4, function calling, embeddings)
- Prompt engineering (few-shot, chain-of-thought)
- Vector databases (Pinecone, Weaviate, pgvector)
- Python ML libraries (numpy, pandas, scikit-learn)
- Fine-tuning LLMs (LoRA, QLoRA)
- Evaluation metrics (BLEU, ROUGE, human-in-the-loop)

**Nice-to-Have:**
- Hugging Face Transformers
- Whisper/AssemblyAI integration
- Speaker diarization (Pyannote)
- Guardrails (NeMo, Llama Guard)
- LLMOps (Weights & Biases, MLflow)

**Interview Test:**
- Build a RAG system for a custom knowledge base
- Optimize token usage for a multi-step agent
- Debug hallucination in a lead generation agent

---

### **5. Data Scientist (Graph Specialist)**

**Must-Have:**
- Neo4j/Cypher queries (MATCH, MERGE, aggregations)
- Graph algorithms (PageRank, Community Detection, Shortest Path)
- NetworkX (Python graph library)
- Graph ML (Node2Vec, GraphSAGE, GNNs)
- Similarity metrics (cosine, Jaccard, graph edit distance)
- Recommendation systems (collaborative filtering, content-based)
- Python data stack (pandas, numpy, matplotlib)

**Nice-to-Have:**
- Neo4j Graph Data Science (GDS) library
- Deep Graph Library (DGL)
- Graph embeddings
- Link prediction
- Knowledge graphs

**Interview Test:**
- Design a matching algorithm for Lyncsea (needs vs. offerings)
- Implement a recommendation system using graph features
- Analyze a social network dataset (centrality, communities)

---

### **6. Product Manager**

**Must-Have:**
- User research (interviews, surveys, A/B testing)
- Feature prioritization (RICE, MoSCoW)
- PRD writing (user stories, acceptance criteria)
- Analytics (Mixpanel, Amplitude, Google Analytics)
- Roadmap planning (OKRs, quarterly goals)
- Stakeholder management
- Technical background (can read code, understand APIs)

**Nice-to-Have:**
- SQL (can query data directly)
- Design thinking
- Growth hacking
- Competitor analysis

**Interview Test:**
- Prioritize 5 features with limited resources
- Write a PRD for a new feature
- Analyze user churn and propose solutions

---

## 📅 18-MONTH HIRING TIMELINE

```
Month 0-3: Bootstrap (2-3 people)
├── Full-Stack Dev (hire immediately)
└── AI/ML part-time (you or contractor)

Month 3-6: Product-Market Fit (5 people)
├── Frontend Engineer
├── Backend Engineer
├── AI/ML Engineer (full-time)
└── DevOps (contractor → part-time)

Month 6-9: Growth (7 people)
├── +1 Data Scientist (Neo4j specialist)
├── +1 QA Engineer
└── +1 Product Manager (part-time)

Month 9-12: Scaling (10 people)
├── +1 Senior Backend Engineer
├── +1 ML Engineer
└── +1 UI/UX Designer

Month 12-18: Maturity (15 people)
├── +1 DevOps Lead
├── +1 Junior Frontend
├── +2 Backend Engineers
└── +1 QA Lead
```

---

## 🚨 CRITICAL DECISIONS TO MAKE NOW

### **1. Deploy Neo4j This Month**
- **Why:** Your matching logic will hit performance walls with PostgreSQL JOINs
- **How:** Neo4j Aura free tier (good for 1,000 users)
- **Cost:** $0-$200/month initially

### **2. Fix DevOps (No More Screen Sessions!)**
- **Current:** Manually SSH to EC2, run `screen -r backend-start`, Ctrl+C, restart
- **Problem:** No rollbacks, no monitoring, no auto-scaling, single point of failure
- **Solution:**
  - Week 1: Dockerize backend + frontend
  - Week 2: Set up GitHub Actions for CI/CD
  - Week 3: Deploy to AWS ECS Fargate (or Render.com for simplicity)
  - Week 4: Add monitoring (Sentry + Datadog)
- **Cost:** $200-$500/month (vs. $50 for manual EC2)

### **3. Hire a Full-Stack Dev NOW**
- **Why:** You need to focus on AI/product, not bug fixes
- **Budget:** ₹1L-₹1.5L/month ($1,250-$1,875)
- **Where:** AngelList, Instahyre, TopHire (India), LinkedIn
- **Test:** Give them a take-home project (fix the Safari audio recording bug)

### **4. Switch to Usage-Based Pricing**
- **Current risk:** Flat $29/month = users can abuse (unlimited recordings)
- **Better:** $19 base + $0.10/minute transcribed
- **Why:** Aligns cost (AssemblyAI charges you per minute) with revenue

---

## 💡 COST OPTIMIZATION STRATEGIES

### **Reduce AI Costs (Currently 30-50% of expenses):**
1. **Cache transcriptions** - Don't re-transcribe the same audio
2. **Use Whisper (open-source)** instead of AssemblyAI for low-priority users
   - AssemblyAI: $0.25/min
   - Whisper (self-hosted): ~$0.05/min
3. **Quantize prompts** - Use GPT-4o-mini ($0.15/1M tokens) instead of GPT-4 ($10/1M tokens) for 90% of tasks
4. **Batch requests** - Send 10 lead extractions in one API call instead of 10 separate calls

### **Reduce Infrastructure Costs:**
1. **Use AWS Reserved Instances** (50% discount for 1-year commitment)
2. **CloudFront caching** - Serve static assets from CDN (save on EC2 bandwidth)
3. **S3 Intelligent Tiering** - Move old recordings to Glacier (95% cheaper)
4. **Auto-scaling** - Turn off dev/staging environments at night (save $200/month)

---

## 📈 SUCCESS METRICS BY STAGE

### **Phase 1 (0-100 users):**
- [ ] < 1% audio recording failures
- [ ] < 5% transcription errors (WER)
- [ ] 99% uptime (deploy from screen → Docker)
- [ ] User retention: 40%+ week-over-week

### **Phase 2 (100-1,000 users):**
- [ ] < 2s median API response time
- [ ] 10+ leads per recording (AI quality)
- [ ] Neo4j matching: 80%+ accuracy
- [ ] User retention: 60%+ month-over-month
- [ ] NPS score: 40+

### **Phase 3 (1,000-10,000 users):**
- [ ] 99.9% uptime (multi-region)
- [ ] < 500ms P95 latency
- [ ] $5-$10 CAC (customer acquisition cost)
- [ ] 3:1 LTV:CAC ratio
- [ ] 25%+ viral coefficient (referrals)

---

## 🎯 FINAL RECOMMENDATIONS

### **Immediate Actions (This Week):**
1. ✅ Hire a Full-Stack Dev (₹1L-₹1.5L/month)
2. ✅ Deploy Neo4j Aura (free tier)
3. ✅ Set up error tracking (Sentry - free tier)
4. ✅ Dockerize backend + frontend

### **Next 30 Days:**
1. ✅ Integrate Neo4j for matching API
2. ✅ Set up CI/CD with GitHub Actions
3. ✅ Deploy to AWS ECS or Render.com
4. ✅ Add usage-based pricing

### **Next 90 Days:**
1. ✅ Hire AI/ML Engineer (full-time)
2. ✅ Hire DevOps contractor (part-time)
3. ✅ Build mobile app MVP (React Native)
4. ✅ Reach 100 paying users

---

## 📞 RECRUITING SOURCES

### **India (Cost-Effective):**
- **AngelList India** - Startups, equity-minded candidates
- **Instahyre** - Pre-vetted engineers (₹80k-₹3L range)
- **TopHire** - Senior engineers (₹2L-₹5L range)
- **Naukri/LinkedIn** - Mass hiring (filter carefully)
- **Referrals** - Best quality, offer ₹20k-₹50k referral bonus

### **Global (High-Quality):**
- **Toptal** - Top 3% freelancers ($60-$200/hour)
- **Upwork** - AI/ML specialists (cheaper but hit-or-miss)
- **Turing.com** - Remote engineers (vetted, $40-$80/hour)

### **Interns (Low-Cost Testing):**
- **AngelList** - Startup enthusiasts
- **IIIT/IIT job portals** - Top talent, ₹20k-₹40k/month

---

**Created:** 2025-01-17
**Next Review:** After reaching 100 users
**Owner:** Lyncsea Founding Team