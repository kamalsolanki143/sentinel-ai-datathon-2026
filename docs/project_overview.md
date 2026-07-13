# Sentinel AI — Project Overview

## AI-Powered Crime Intelligence & Decision Operating System

---

## 1. Executive Summary

**Sentinel AI** is an enterprise-grade, AI-powered Crime Intelligence and Decision Operating System designed to transform how law enforcement agencies analyze crime data, predict future incidents, investigate cases, and allocate resources. Built for the **AI Datathon 2026**, Sentinel AI combines cutting-edge machine learning, knowledge graph technology, and multi-agent AI orchestration to deliver actionable crime intelligence in real time.

### Vision Statement

> *"To empower law enforcement with an intelligent operating system that transforms raw crime data into predictive insights, automated investigations, and optimized resource deployment — saving lives through the power of AI."*

### Problem Statement

Indian law enforcement agencies face critical challenges:

- **Data Overload**: Thousands of FIRs, complaints, and reports generated daily across districts with no unified intelligence layer.
- **Reactive Policing**: Officers respond to crimes after they occur rather than preventing them proactively.
- **Disconnected Systems**: Crime records, suspect databases, and patrol schedules exist in silos with no cross-referencing.
- **Manual Analysis**: Crime pattern detection, hotspot identification, and resource allocation rely on human intuition rather than data-driven insights.
- **Investigation Bottlenecks**: Complex cases involving multiple suspects, locations, and evidence chains overwhelm manual investigation workflows.

### Solution

Sentinel AI addresses these challenges through six core capabilities:

| Capability | Description |
|---|---|
| **Crime Intelligence** | Real-time crime analytics with statistical analysis, trend detection, and pattern recognition |
| **Predictive Policing** | ML-powered hotspot prediction, crime forecasting, and anomaly detection |
| **AI Investigation** | Multi-agent AI system that automates evidence analysis, suspect profiling, and case reconstruction |
| **Knowledge Graph** | Neo4j-powered criminal network analysis, entity resolution, and relationship mapping |
| **Resource Optimization** | Officer recommendation engine with patrol routing and workload balancing |
| **Simulation Engine** | What-if scenario modeling for crime prevention strategy evaluation |

---

## 2. High-Level System Architecture

```mermaid
graph TB
    subgraph Frontend["🖥️ Frontend (Next.js + React + TypeScript)"]
        UI[Dashboard UI]
        Maps[Crime Maps]
        Charts[Analytics Charts]
        Chat[AI Chat Interface]
        Reports[Report Viewer]
    end

    subgraph API["⚡ API Layer (FastAPI)"]
        CrimesAPI[Crimes API]
        PredictionsAPI[Predictions API]
        AnalyticsAPI[Analytics API]
        ChatAPI[Chat API]
        ReportsAPI[Reports API]
        SimulationAPI[Simulation API]
        NetworkAPI[Network API]
        RecommendationsAPI[Recommendations API]
    end

    subgraph Agents["🤖 AI Agent Layer (LangGraph + Gemini)"]
        Orchestrator[Orchestrator Agent]
        InvestAgent[Investigation Agent]
        AnalyticsAgent[Analytics Agent]
        PredictionAgent[Prediction Agent]
        GraphAgent[Graph Agent]
        RecommendAgent[Recommendation Agent]
        ReportAgent[Report Agent]
        SimAgent[Simulation Agent]
    end

    subgraph ML["🧠 Machine Learning"]
        Hotspot[Hotspot Prediction]
        Forecast[Crime Forecasting]
        Anomaly[Anomaly Detection]
        Recommend[Recommendation Models]
    end

    subgraph Analytics["📊 Analytics Engine"]
        Stats[Crime Statistics]
        Trends[Trend Analysis]
        HotspotA[Hotspot Analysis]
        District[District Analysis]
        Patterns[Crime Patterns]
        Risk[Risk Scoring]
        ReportGen[Report Generator]
    end

    subgraph Data["🗄️ Data Layer"]
        PG[(PostgreSQL)]
        Neo[(Neo4j)]
    end

    Frontend --> API
    API --> Agents
    API --> Analytics
    Agents --> ML
    Agents --> Data
    Analytics --> Data
    ML --> Data
    Orchestrator --> InvestAgent
    Orchestrator --> AnalyticsAgent
    Orchestrator --> PredictionAgent
    Orchestrator --> GraphAgent
    Orchestrator --> RecommendAgent
    Orchestrator --> ReportAgent
    Orchestrator --> SimAgent
```

---

## 3. Module Breakdown

### 3.1 Frontend Module

| Component | Technology | Purpose |
|---|---|---|
| Dashboard | Next.js + React | Main command center with real-time crime metrics |
| Crime Maps | Leaflet / Mapbox | Interactive geospatial crime visualization |
| Analytics Charts | Recharts / D3.js | Statistical visualizations and trend graphs |
| AI Chat | WebSocket + React | Natural language crime intelligence queries |
| Report Viewer | PDF.js + React | View and export generated reports |

### 3.2 Backend API Module

| Endpoint Group | Purpose | Key Routes |
|---|---|---|
| `/api/crimes` | Crime data CRUD | GET, POST, PUT, DELETE crime records |
| `/api/predictions` | ML predictions | Hotspot maps, crime forecasts, anomalies |
| `/api/chat` | AI conversation | Natural language queries to agent system |
| `/api/reports` | Report management | Generate, retrieve, export reports |
| `/api/network` | Graph operations | Criminal networks, entity relationships |
| `/api/recommendations` | Resource allocation | Officer assignments, patrol routes |
| `/api/simulation` | Scenario modeling | What-if analysis, impact assessment |

### 3.3 AI Agent Module

```mermaid
graph LR
    subgraph Orchestrator["🎯 Orchestrator"]
        IC[Intent Classifier]
        Router[Agent Router]
        Agg[Result Aggregator]
    end

    subgraph Specialists["Specialist Agents"]
        IA[Investigation Agent]
        AA[Analytics Agent]
        PA[Prediction Agent]
        GA[Graph Agent]
        RA[Recommendation Agent]
        ReA[Report Agent]
        SA[Simulation Agent]
    end

    IC --> Router
    Router --> IA
    Router --> AA
    Router --> PA
    Router --> GA
    Router --> RA
    Router --> ReA
    Router --> SA
    IA --> Agg
    AA --> Agg
    PA --> Agg
    GA --> Agg
    RA --> Agg
    ReA --> Agg
    SA --> Agg
```

| Agent | Responsibility | Key Integrations |
|---|---|---|
| **Orchestrator** | Routes requests to specialist agents, aggregates results | All agents, LangGraph |
| **Investigation** | Automated case investigation and evidence analysis | Neo4j, PostgreSQL, Gemini |
| **Analytics** | Statistical analysis and insight generation | Analytics module, Gemini |
| **Prediction** | ML model orchestration and risk assessment | ML module, Gemini |
| **Graph** | Knowledge graph queries and network analysis | Neo4j, Gemini |
| **Recommendation** | Resource allocation and deployment optimization | ML recommender, Gemini |
| **Report** | Automated report generation | All agents, Gemini |
| **Simulation** | Crime scenario modeling and impact analysis | ML models, Gemini |

### 3.4 Machine Learning Module

| Sub-Module | Models | Purpose |
|---|---|---|
| **Hotspot Prediction** | Random Forest, Gradient Boosting | Predict crime concentration zones |
| **Crime Forecasting** | Time-series regression, lag-based models | Forecast crime counts by district/type |
| **Anomaly Detection** | Isolation Forest, statistical methods | Detect unusual crime patterns |
| **Recommendation** | Multi-criteria scoring, constraint satisfaction | Optimize officer-to-case assignments |

### 3.5 Analytics Module

| Component | Purpose |
|---|---|
| **Crime Statistics** | Descriptive statistics, counts, rates, distributions |
| **Trend Analysis** | Temporal trends, seasonal patterns, change-point detection |
| **Hotspot Analysis** | Spatial density analysis, DBSCAN clustering |
| **District Analysis** | Per-district metrics, comparative performance |
| **Crime Patterns** | MO analysis, serial crime identification |
| **Risk Scoring** | Multi-factor composite risk scores |
| **Report Generator** | Automated report templates with data injection |

### 3.6 Data Layer

| Database | Purpose | Key Use Cases |
|---|---|---|
| **PostgreSQL** | Relational data storage | Crime records, officer data, case files, predictions, reports |
| **Neo4j** | Graph database | Criminal networks, suspect relationships, evidence chains, entity resolution |

---

## 4. Technology Stack

```mermaid
graph TD
    subgraph Frontend
        NextJS[Next.js 14]
        React[React 18]
        TS[TypeScript]
        Tailwind[Tailwind CSS]
    end

    subgraph Backend
        FastAPI[FastAPI]
        Python[Python 3.11+]
        Uvicorn[Uvicorn ASGI]
    end

    subgraph AI
        Gemini[Gemini API]
        LangChain[LangChain]
        LangGraph[LangGraph]
    end

    subgraph MLStack["Machine Learning"]
        Pandas[Pandas]
        NumPy[NumPy]
        Sklearn[Scikit-learn]
        Joblib[Joblib]
    end

    subgraph Database
        PG[(PostgreSQL 15)]
        Neo4j[(Neo4j 5.x)]
    end

    subgraph Infra["Infrastructure"]
        Docker[Docker]
        DockerCompose[Docker Compose]
    end

    Frontend --> Backend
    Backend --> AI
    Backend --> MLStack
    Backend --> Database
    Infra --> Frontend
    Infra --> Backend
    Infra --> Database
```

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | Next.js | 14.x | Server-side rendering, routing |
| | React | 18.x | Component-based UI |
| | TypeScript | 5.x | Type-safe frontend code |
| | Tailwind CSS | 3.x | Utility-first styling |
| **Backend** | FastAPI | 0.104+ | Async REST API framework |
| | Python | 3.11+ | Core backend language |
| | Uvicorn | 0.24+ | ASGI server |
| **AI** | Gemini API | 2.0 | Large Language Model |
| | LangChain | 0.2+ | LLM framework |
| | LangGraph | 0.2+ | Agent orchestration |
| **ML** | Pandas | 2.x | Data manipulation |
| | NumPy | 1.26+ | Numerical computing |
| | Scikit-learn | 1.4+ | ML algorithms |
| **Database** | PostgreSQL | 15.x | Relational storage |
| | Neo4j | 5.x | Graph database |
| **Infrastructure** | Docker | 24.x | Containerization |
| | Docker Compose | 2.x | Multi-container orchestration |

---

## 5. Data Flow Overview

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚡ FastAPI
    participant Orch as 🎯 Orchestrator
    participant Agent as 🤖 Agent
    participant ML as 🧠 ML Models
    participant PG as 🗄️ PostgreSQL
    participant Neo as 🔗 Neo4j
    participant Gemini as 🌟 Gemini API

    User->>FE: Interaction (query/click)
    FE->>API: HTTP/WebSocket Request
    API->>Orch: Route to AI System
    Orch->>Orch: Classify Intent
    Orch->>Agent: Delegate to Specialist
    Agent->>PG: Query Crime Data
    PG-->>Agent: Structured Results
    Agent->>Neo: Query Relationships
    Neo-->>Agent: Graph Results
    Agent->>ML: Request Predictions
    ML-->>Agent: ML Results
    Agent->>Gemini: Generate Insights
    Gemini-->>Agent: AI Analysis
    Agent-->>Orch: Agent Results
    Orch-->>API: Aggregated Response
    API-->>FE: JSON Response
    FE-->>User: Rendered Results
```

---

## 6. Key Differentiators

| Feature | Traditional Systems | Sentinel AI |
|---|---|---|
| **Analysis** | Manual, retrospective | AI-powered, predictive |
| **Investigation** | Single-officer, linear | Multi-agent, parallel |
| **Data Integration** | Siloed databases | Unified knowledge graph |
| **Resource Allocation** | Experience-based | ML-optimized |
| **Reporting** | Manual, template-based | AI-generated, contextual |
| **Scenario Planning** | Ad-hoc meetings | Simulation engine |

---

## 7. Project Structure

```
sentinel-ai-datathon-2026/
├── frontend/                  # Next.js frontend application
│   ├── src/
│   │   ├── app/              # Next.js app router pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utility libraries
│   └── package.json
├── backend/                   # FastAPI backend
│   ├── agents/               # LangGraph AI agents
│   │   ├── orchestrator.py   # Master agent coordinator
│   │   ├── investigation_agent.py
│   │   ├── analytics_agent.py
│   │   ├── prediction_agent.py
│   │   ├── graph_agent.py
│   │   ├── recommendation_agent.py
│   │   ├── report_agent.py
│   │   ├── simulation_agent.py
│   │   └── prompts.py        # Centralized prompts
│   ├── api/                  # FastAPI route handlers
│   ├── database/             # Database connectors
│   ├── models/               # Pydantic data models
│   └── main.py               # Application entry point
├── ml/                        # Machine learning modules
│   ├── hotspot_prediction/   # Crime hotspot ML
│   ├── crime_forecasting/    # Time-series forecasting
│   ├── anomaly_detection/    # Anomaly detection
│   ├── recommendation_models/ # Officer recommendation
│   └── utils/                # Shared ML utilities
├── analytics/                 # Analytics engine
│   ├── crime_statistics.py
│   ├── trend_analysis.py
│   ├── hotspot_analysis.py
│   ├── district_analysis.py
│   ├── crime_pattern.py
│   ├── risk_score.py
│   └── report_generator.py
├── datasets/                  # Data files
│   ├── raw/                  # Raw datasets
│   └── processed/            # Processed datasets
├── docs/                      # Documentation
├── architecture/              # Architecture diagrams
├── research/                  # Research notes
├── docker-compose.yml         # Container orchestration
└── requirements.txt           # Python dependencies
```

---

## 8. Deployment Architecture

```mermaid
graph TB
    subgraph Docker["🐳 Docker Compose"]
        subgraph FrontendContainer["Frontend Container"]
            NextApp[Next.js App :3000]
        end

        subgraph BackendContainer["Backend Container"]
            FastAPIApp[FastAPI App :8000]
        end

        subgraph DBContainers["Database Containers"]
            PostgresDB[(PostgreSQL :5432)]
            Neo4jDB[(Neo4j :7474/:7687)]
        end
    end

    Client[🌐 Browser] --> NextApp
    NextApp --> FastAPIApp
    FastAPIApp --> PostgresDB
    FastAPIApp --> Neo4jDB
    FastAPIApp --> GeminiCloud[☁️ Gemini API]
```

---

## 9. Success Metrics

| Metric | Target |
|---|---|
| Hotspot prediction accuracy | ≥ 85% |
| Crime forecast MAE | ≤ 15% |
| Anomaly detection precision | ≥ 80% |
| Agent response time | < 5 seconds |
| System uptime | 99.9% |
| Report generation time | < 10 seconds |

---

*Sentinel AI — Transforming Crime Data into Actionable Intelligence*
