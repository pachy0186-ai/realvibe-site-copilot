# RealVibe Site Copilot

AI-powered clinical trial feasibility questionnaire auto-fill SaaS that enables research sites to automatically complete sponsor questionnaires using their private "answer memory" with evidence links back to original files.

## 🎯 North-Star Outcome

Enable 3 pilot sites to complete ≥10 feasibility packets each with:
- ≥60% auto-fill rate
- ≤15 min median review time  
- ≥2 weeks cycle-time reduction vs. baseline

## 🏗️ Architecture

### Monorepo Structure
```
realvibe-site-copilot/
├── backend/          # FastAPI backend with AI agents
├── frontend/         # Next.js frontend
├── infra/           # Infrastructure and deployment configs
└── docs/            # Documentation
```

### Tech Stack
- **Backend**: Python, FastAPI, CrewAI/LangGraph agents
- **Database**: Supabase (Postgres + pgvector for semantic search)
- **Frontend**: Next.js, deployed on Vercel
- **Storage**: Supabase Storage for file uploads
- **Deployment**: Vercel (frontend), Supabase (backend + DB)

## 🤖 AI Agent Pipeline

**Planner** → **Retriever** → **Mapper** → **Evidencer** → **Filler** → **QA** → **Recorder**

### Agent Tools
- `memory.search` - Hybrid keyword + vector search
- `memory.upsert` - Update canonical field values + provenance  
- `pdf.parse` and `pdf.fill` - PDF processing
- `rules.validate` - Cross-field QA
- `notify.reviewer` - Gmail integration

## 📊 Database Schema

- **sites** - Research site information
- **files** - Uploaded documents with metadata
- **chunks** - Text chunks with embeddings for search
- **answer_memory** - Canonical answers with provenance
- **questionnaire_templates** - Sponsor questionnaire schemas
- **runs** - Autofill execution records
- **answers** - Individual field answers with evidence

## 🔒 Security & Privacy

- Row-level security ensures each site only sees its own data
- Private answer memory per site
- Evidence provenance tracking for audit trails
- Never guess values - mark "Needs Review" when confidence is low

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/pachy0186-ai/realvibe-site-copilot.git
cd realvibe-site-copilot
```

2. Set up backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up frontend:
```bash
cd frontend
npm install
```

4. Configure environment variables (see `.env.example` files)

5. Run development servers:
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend  
cd frontend && npm run dev
```

## 📈 Key Metrics

For each autofill run, the system tracks:
- **Autofill %** - Percentage of fields automatically filled
- **Review Time** - Minutes spent by reviewers
- **Cycle-time Delta** - Time savings vs baseline manual process

## 🔗 Domain Strategy

Deployed under main domain: `realvibeai.com/site-copilot`

## 📝 License

[License information]

## 🤝 Contributing

[Contributing guidelines]

