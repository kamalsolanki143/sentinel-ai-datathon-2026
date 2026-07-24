# Sentinel AI 🛡️
### AI-Powered Crime Intelligence & Decision Operating System

**Sentinel AI** is an enterprise-grade AI decision operating system that empowers police departments, command centers, and public safety organizations to make intelligent operational decisions. By synthesizing multi-agent AI frameworks, machine learning hotspot models, Neo4j Knowledge Graphs, Operations Research optimization, and Gemini AI explainable intelligence, Sentinel AI turns complex crime data into actionable, prioritized operational strategy.

---

## 🚀 Key Subsystems & Features

- 🎯 **Officer Deployment Recommendation Engine**: Multi-criteria scoring matching officer expertise, workload, fatigue, and location to high-risk crime hotspots.
- 🚏 **Patrol Route Optimization (TSP 2-Opt)**: Graph-based route solver minimizing travel distance and response time while maximizing high-risk sector coverage.
- 🧮 **Multi-Resource Allocation (Hungarian Algorithm)**: Linear sum assignment optimization matching Officers, Patrol Vehicles, SWAT/Tactical Teams, Cyber Units, and Emergency Units.
- ⚖️ **Policy Rules & Safety Engine**: Evaluates mandatory duo dispatch rules, $12\text{-hour}$ shift fatigue limits, station boundary limits, and vehicle fuel levels.
- 🧠 **Multi-Agent LangGraph System**: Integrated Prediction, Analytics, Graph Intelligence, Simulation, and Recommendation Agents.
- 💬 **Sentinel Copilot**: RAG-powered conversational assistant for real-time tactical queries.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, Loguru, SQLAlchemy, AsyncPG
- **AI & LLM**: Google Gemini API, LangChain, LangGraph
- **Databases**: PostgreSQL (Async), Neo4j Knowledge Graph, Vector DB RAG Index
- **Operations Research & ML**: Scikit-Learn, SciPy (Hungarian Algorithm), NumPy, Pandas
- **Frontend**: Next.js, React, Tailwind CSS

---

## ⚡ Quick Start & Deployment

### 1. Environment Configuration
Copy `.env.example` to `.env` and set your API keys:
```bash
cp .env.example .env
```
Ensure `GOOGLE_API_KEY` is configured.

### 2. Local Backend Run
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Docker Compose Deployment
```bash
docker-compose up -d --build
```
Access points:
- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Neo4j Browser**: `http://localhost:7474`

---

## 🌐 REST API Endpoints Overview

| Category | Endpoint | Description |
| :--- | :--- | :--- |
| **Recommendations** | `POST /api/v1/recommendations/officer-deployment` | Recommend officer assignments |
| **Recommendations** | `POST /api/v1/recommendations/patrol-routes` | Generate TSP 2-Opt patrol route plans |
| **Recommendations** | `POST /api/v1/recommendations/resource-allocation` | Run Hungarian multi-resource allocation |
| **Recommendations** | `POST /api/v1/recommendations/risk-prioritization` | Rank hotspots and CAD incidents |
| **Recommendations** | `POST /api/v1/recommendations/full-strategy` | Master crime response strategy + Gemini AI rationale |
| **Copilot Chat** | `POST /api/v1/chat/query` | Conversational RAG Copilot query |
| **Predictions** | `POST /api/v1/predictions/hotspots` | ML hotspot predictions |
| **Network** | `POST /api/v1/network/analyze` | Neo4j criminal network graph analysis |
| **Simulation** | `POST /api/v1/simulation/run` | Monte Carlo patrol scenario simulation |
| **Reports** | `POST /api/v1/reports/generate` | Automated intelligence report generation |

---

## 📜 License
Released under the MIT License.
