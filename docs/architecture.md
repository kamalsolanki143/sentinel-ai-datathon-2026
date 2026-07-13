# Sentinel AI — System Architecture

## Comprehensive Architecture Documentation

---

## 1. Architecture Overview

Sentinel AI follows a **layered microservices-inspired architecture** with clear separation of concerns. The system is designed around four primary layers, each with well-defined responsibilities and interfaces.

```mermaid
graph TB
    subgraph PresentationLayer["📱 Presentation Layer"]
        direction LR
        Dashboard[Dashboard]
        CrimeMap[Crime Map]
        AIChat[AI Chat]
        ReportView[Reports]
        SimView[Simulation]
    end

    subgraph APILayer["⚡ API Gateway Layer"]
        direction LR
        REST[REST Endpoints]
        WS[WebSocket Handler]
        Auth[Authentication]
        RateLimit[Rate Limiter]
        Validator[Request Validator]
    end

    subgraph BusinessLayer["🧠 Business Logic Layer"]
        direction TB
        subgraph AgentSystem["AI Agent System"]
            Orch[Orchestrator]
            Agents[Specialist Agents x7]
        end
        subgraph AnalyticsEngine["Analytics Engine"]
            StatEngine[Statistics Engine]
            TrendEngine[Trend Engine]
            PatternEngine[Pattern Engine]
        end
        subgraph MLPipeline["ML Pipeline"]
            Training[Training Pipeline]
            Inference[Inference Pipeline]
            FeatureStore[Feature Store]
        end
    end

    subgraph DataLayer["🗄️ Data Access Layer"]
        direction LR
        PGConn[PostgreSQL Connector]
        NeoConn[Neo4j Connector]
        ModelStore[Model Storage]
        Cache[Cache Layer]
    end

    subgraph StorageLayer["💾 Storage Layer"]
        direction LR
        PG[(PostgreSQL)]
        Neo[(Neo4j)]
        FS[File System]
    end

    PresentationLayer --> APILayer
    APILayer --> BusinessLayer
    BusinessLayer --> DataLayer
    DataLayer --> StorageLayer
```

---

## 2. Layer Architecture

### 2.1 Presentation Layer (Frontend)

**Technology**: Next.js 14, React 18, TypeScript, Tailwind CSS

```mermaid
graph TD
    subgraph NextApp["Next.js Application"]
        AppRouter[App Router]

        subgraph Pages
            DashboardPage["/dashboard"]
            MapPage["/map"]
            InvestigatePage["/investigate"]
            AnalyticsPage["/analytics"]
            ReportsPage["/reports"]
            SimulationPage["/simulation"]
            ChatPage["/chat"]
        end

        subgraph SharedComponents
            Navbar[Navigation Bar]
            Sidebar[Sidebar Menu]
            ChartLib[Chart Components]
            MapLib[Map Components]
            TableLib[Data Tables]
            FormLib[Form Components]
        end

        subgraph StateManagement
            APIClient[API Client Layer]
            WSClient[WebSocket Client]
            LocalState[React State / Context]
        end

        AppRouter --> Pages
        Pages --> SharedComponents
        Pages --> StateManagement
    end
```

**Key Design Decisions**:

| Decision | Choice | Rationale |
|---|---|---|
| Rendering | Server-side (SSR) | SEO + fast initial load for dashboards |
| State | React Context + local state | Sufficient for dashboard app, no Redux overhead |
| API Communication | Fetch API + WebSocket | REST for CRUD, WebSocket for real-time chat |
| Styling | Tailwind CSS | Rapid development, consistent design system |
| Charts | Recharts | React-native charting, lightweight |
| Maps | Leaflet | Open-source, no API key required |

---

### 2.2 API Gateway Layer (Backend)

**Technology**: FastAPI, Python 3.11+, Uvicorn

```mermaid
graph LR
    subgraph FastAPIApp["FastAPI Application"]
        subgraph Middleware
            CORS[CORS Middleware]
            ErrorHandler[Error Handler]
            Logger[Request Logger]
        end

        subgraph Routers
            CrimeRouter["/api/crimes"]
            PredRouter["/api/predictions"]
            ChatRouter["/api/chat"]
            ReportRouter["/api/reports"]
            NetworkRouter["/api/network"]
            RecommRouter["/api/recommendations"]
            SimRouter["/api/simulation"]
        end

        subgraph Dependencies
            DBSession[DB Session Provider]
            AuthDep[Auth Dependency]
            ConfigDep[Config Provider]
        end

        Middleware --> Routers
        Routers --> Dependencies
    end
```

**API Design Principles**:

- **RESTful conventions**: Standard HTTP methods, proper status codes, consistent response schemas
- **Async-first**: All route handlers are `async def` for non-blocking I/O
- **Dependency Injection**: FastAPI's `Depends()` for database sessions, auth, and config
- **Pydantic Models**: Request/response validation with Pydantic v2
- **Error Handling**: Global exception handlers with structured error responses
- **CORS**: Configured for frontend origin in development and production

**Endpoint Architecture**:

| Router | Method | Endpoint | Description |
|---|---|---|---|
| `crimes` | GET | `/api/crimes` | List crimes with filters |
| | GET | `/api/crimes/{id}` | Get crime details |
| | POST | `/api/crimes` | Create crime record |
| `predictions` | GET | `/api/predictions/hotspots` | Get hotspot predictions |
| | GET | `/api/predictions/forecast` | Get crime forecasts |
| | GET | `/api/predictions/anomalies` | Get detected anomalies |
| `chat` | POST | `/api/chat` | Send message to AI system |
| | WebSocket | `/api/chat/ws` | Real-time AI conversation |
| `reports` | GET | `/api/reports` | List generated reports |
| | POST | `/api/reports/generate` | Generate new report |
| `network` | GET | `/api/network/graph` | Get criminal network graph |
| | GET | `/api/network/entity/{id}` | Get entity relationships |
| `recommendations` | GET | `/api/recommendations/officers` | Get officer recommendations |
| | GET | `/api/recommendations/patrols` | Get patrol route suggestions |
| `simulation` | POST | `/api/simulation/run` | Run crime simulation |
| | GET | `/api/simulation/{id}` | Get simulation results |

---

### 2.3 Business Logic Layer

This layer contains the core intelligence of Sentinel AI, divided into three sub-systems.

#### 2.3.1 AI Agent System (LangGraph + Gemini)

```mermaid
stateDiagram-v2
    [*] --> IntentClassification
    IntentClassification --> AgentRouting

    state AgentRouting {
        [*] --> SelectAgents
        SelectAgents --> ParallelExecution: Multiple agents needed
        SelectAgents --> SingleExecution: Single agent needed

        state ParallelExecution {
            [*] --> fork_state
            fork_state --> Agent1
            fork_state --> Agent2
            fork_state --> Agent3
            Agent1 --> join_state
            Agent2 --> join_state
            Agent3 --> join_state
        }

        state SingleExecution {
            [*] --> TargetAgent
            TargetAgent --> [*]
        }

        ParallelExecution --> [*]
    }

    AgentRouting --> ResultAggregation
    ResultAggregation --> ResponseGeneration
    ResponseGeneration --> [*]
```

**Agent Communication Protocol**:

Each agent operates as a LangGraph node within a state machine. Agents communicate through a shared `AgentState` (TypedDict) that flows through the graph:

```python
class AgentState(TypedDict):
    messages: list              # Conversation history
    query: str                  # User query
    intent: str                 # Classified intent
    context: dict               # Shared context data
    crime_data: list            # Crime records from PostgreSQL
    graph_data: dict            # Relationships from Neo4j
    ml_predictions: dict        # ML model outputs
    analytics_results: dict     # Analytics computations
    recommendations: list       # Resource recommendations
    simulation_results: dict    # Simulation outputs
    report: dict                # Generated report data
    errors: list                # Error tracking
    metadata: dict              # Processing metadata
```

**Agent Responsibilities**:

| Agent | Input | Processing | Output |
|---|---|---|---|
| **Orchestrator** | User query | Intent classification, agent routing | Aggregated response |
| **Investigation** | Case ID / evidence | Evidence analysis, timeline reconstruction | Investigation report |
| **Analytics** | Crime data filters | Statistical analysis, pattern detection | Analytics insights |
| **Prediction** | Location / time range | ML model invocation, risk assessment | Predictions + risk scores |
| **Graph** | Entity IDs / query | Neo4j traversal, network analysis | Relationship maps |
| **Recommendation** | Constraints / context | Scoring, optimization | Officer assignments |
| **Report** | Multi-agent results | Data aggregation, narrative generation | Structured report |
| **Simulation** | Scenario parameters | Monte Carlo simulation, impact modeling | Scenario outcomes |

#### 2.3.2 Analytics Engine

```mermaid
graph TD
    subgraph AnalyticsEngine["Analytics Engine"]
        CS[Crime Statistics] --> TA[Trend Analysis]
        CS --> HA[Hotspot Analysis]
        CS --> DA[District Analysis]
        TA --> CP[Crime Patterns]
        HA --> CP
        DA --> CP
        CP --> RS[Risk Scoring]
        RS --> RG[Report Generator]
        CS --> RG
        TA --> RG
        HA --> RG
        DA --> RG
    end

    PG[(PostgreSQL)] --> CS
    PG --> DA
    Neo[(Neo4j)] --> CP
    Neo --> HA
```

| Module | Data Source | Key Operations |
|---|---|---|
| **Crime Statistics** | PostgreSQL | Counts, rates, distributions, clearance rates |
| **Trend Analysis** | PostgreSQL | Moving averages, seasonal decomposition, change-points |
| **Hotspot Analysis** | PostgreSQL + Neo4j | DBSCAN clustering, spatial density, kernel density estimation |
| **District Analysis** | PostgreSQL | Per-district KPIs, comparative rankings |
| **Crime Patterns** | Neo4j | MO analysis, serial crime detection, relationship patterns |
| **Risk Scoring** | All sources | Composite multi-factor risk scores |
| **Report Generator** | All modules | Template-based report assembly |

#### 2.3.3 ML Pipeline

```mermaid
graph LR
    subgraph DataIngestion["Data Ingestion"]
        Raw[Raw Data] --> Preprocess[Preprocessing]
        Preprocess --> Features[Feature Engineering]
    end

    subgraph Training["Training Pipeline"]
        Features --> Split[Train/Test Split]
        Split --> Train[Model Training]
        Train --> Evaluate[Evaluation]
        Evaluate --> Save[Model Persistence]
    end

    subgraph Inference["Inference Pipeline"]
        NewData[New Data] --> PreprocessInf[Preprocessing]
        PreprocessInf --> FeaturesInf[Feature Extraction]
        FeaturesInf --> LoadModel[Load Model]
        LoadModel --> Predict[Prediction]
        Predict --> PostProcess[Post-Processing]
    end

    Save --> LoadModel
```

---

### 2.4 Data Access Layer

```mermaid
graph TD
    subgraph DAL["Data Access Layer"]
        subgraph PostgresConnector["PostgreSQL Connector"]
            PGPool[Connection Pool]
            PGQuery[Query Builder]
            PGORM[SQL Operations]
        end

        subgraph Neo4jConnector["Neo4j Connector"]
            NeoDriver[Async Driver]
            CypherBuilder[Cypher Builder]
            GraphOps[Graph Operations]
        end

        subgraph ModelStorage["Model Storage"]
            ModelIO[Model I/O]
            VersionControl[Version Tracking]
        end
    end

    PGPool --> PG[(PostgreSQL)]
    NeoDriver --> Neo[(Neo4j)]
    ModelIO --> FS[File System]
```

**PostgreSQL Schema Architecture**:

```mermaid
erDiagram
    CRIMES {
        uuid id PK
        varchar crime_type
        text description
        timestamp occurred_at
        varchar status
        float latitude
        float longitude
        varchar district
        varchar station
        varchar severity
    }

    SUSPECTS {
        uuid id PK
        varchar name
        int age
        varchar gender
        text description
        varchar risk_level
        text known_associates
    }

    OFFICERS {
        uuid id PK
        varchar name
        varchar badge_number
        varchar rank
        varchar station
        varchar specialization
        float workload_score
    }

    EVIDENCE {
        uuid id PK
        uuid crime_id FK
        varchar evidence_type
        text description
        timestamp collected_at
        varchar status
    }

    PREDICTIONS {
        uuid id PK
        varchar prediction_type
        jsonb result_data
        float confidence
        timestamp generated_at
        varchar model_version
    }

    REPORTS {
        uuid id PK
        varchar report_type
        jsonb content
        timestamp generated_at
        varchar generated_by
    }

    CRIMES ||--o{ EVIDENCE : has
    CRIMES ||--o{ SUSPECTS : involves
    OFFICERS ||--o{ CRIMES : assigned_to
    CRIMES ||--o{ PREDICTIONS : generates
    CRIMES ||--o{ REPORTS : included_in
```

**Neo4j Graph Model**:

```mermaid
graph TD
    S1((Suspect A)) -->|ASSOCIATED_WITH| S2((Suspect B))
    S1 -->|COMMITTED| C1[Crime 1]
    S2 -->|COMMITTED| C2[Crime 2]
    C1 -->|OCCURRED_AT| L1{Location X}
    C2 -->|OCCURRED_AT| L1
    C1 -->|HAS_EVIDENCE| E1[Evidence 1]
    S1 -->|LIVES_IN| L2{Location Y}
    C1 -->|SIMILAR_MO| C2
    S1 -->|OWNS| V1[Vehicle 1]
```

**Node Types**: Suspect, Crime, Location, Evidence, Vehicle, Officer, Station
**Relationship Types**: COMMITTED, ASSOCIATED_WITH, OCCURRED_AT, HAS_EVIDENCE, SIMILAR_MO, ASSIGNED_TO, LIVES_IN, OWNS, WITNESSED

---

## 3. Integration Architecture

### 3.1 Gemini API Integration

```mermaid
sequenceDiagram
    participant Agent as AI Agent
    participant LC as LangChain
    participant Gemini as Gemini API

    Agent->>LC: Create ChatGoogleGenerativeAI
    Note over LC: model="gemini-2.0-flash"
    Note over LC: temperature=0.3
    Agent->>LC: Invoke with messages
    LC->>Gemini: API Request (prompt + context)
    Gemini-->>LC: Generated Response
    LC-->>Agent: Parsed Response
    Agent->>Agent: Process & Validate Output
```

**Integration Pattern**:
- LLM initialization via `langchain_google_genai.ChatGoogleGenerativeAI`
- API key from environment variable `GOOGLE_API_KEY`
- Temperature tuned per agent (investigation=0.2, simulation=0.7)
- Structured output parsing with Pydantic models
- Retry logic with exponential backoff on API failures

### 3.2 LangGraph Workflow Architecture

```mermaid
graph TD
    START((Start)) --> IC[Intent Classification]
    IC --> Decision{Route Decision}

    Decision -->|investigation| INV[Investigation Agent]
    Decision -->|analytics| ANA[Analytics Agent]
    Decision -->|prediction| PRED[Prediction Agent]
    Decision -->|graph_query| GRAPH[Graph Agent]
    Decision -->|recommendation| REC[Recommendation Agent]
    Decision -->|simulation| SIM[Simulation Agent]
    Decision -->|report| REP[Report Agent]
    Decision -->|multi_agent| MULTI[Multi-Agent Parallel]

    MULTI --> INV
    MULTI --> ANA
    MULTI --> PRED

    INV --> AGG[Result Aggregation]
    ANA --> AGG
    PRED --> AGG
    GRAPH --> AGG
    REC --> AGG
    SIM --> AGG
    REP --> AGG

    AGG --> RESP[Response Generation]
    RESP --> END((End))
```

### 3.3 RAG Pipeline Architecture

```mermaid
graph LR
    subgraph Ingestion["Document Ingestion"]
        Docs[Crime Documents] --> Chunk[Text Chunking]
        Chunk --> Embed[Embedding Generation]
        Embed --> Store[Vector Storage]
    end

    subgraph Retrieval["Query Pipeline"]
        Query[User Query] --> QEmbed[Query Embedding]
        QEmbed --> Search[Similarity Search]
        Store --> Search
        Search --> Context[Retrieved Context]
    end

    subgraph Generation["Response Generation"]
        Context --> Prompt[Augmented Prompt]
        Query --> Prompt
        Prompt --> LLM[Gemini API]
        LLM --> Response[AI Response]
    end
```

---

## 4. Cross-Module Communication

```mermaid
graph TD
    subgraph Frontend
        FE[React Components]
    end

    subgraph API["FastAPI"]
        Routes[Route Handlers]
    end

    subgraph Agents["Agent Layer"]
        Orch[Orchestrator]
        SpecAgents[Specialist Agents]
    end

    subgraph Analytics
        AnalMods[Analytics Modules]
    end

    subgraph ML
        MLMods[ML Models]
    end

    subgraph DB["Databases"]
        PG[(PostgreSQL)]
        Neo[(Neo4j)]
    end

    FE -->|"HTTP/WS"| Routes
    Routes -->|"async call"| Orch
    Routes -->|"async call"| AnalMods
    Orch -->|"LangGraph state"| SpecAgents
    SpecAgents -->|"function call"| AnalMods
    SpecAgents -->|"function call"| MLMods
    SpecAgents -->|"async query"| PG
    SpecAgents -->|"async query"| Neo
    AnalMods -->|"SQL query"| PG
    AnalMods -->|"Cypher query"| Neo
    MLMods -->|"SQL query"| PG
```

**Communication Protocols**:

| From | To | Protocol | Data Format |
|---|---|---|---|
| Frontend → API | HTTP REST / WebSocket | JSON |
| API → Agents | Async function call | Python dict / TypedDict |
| Orchestrator → Agents | LangGraph state machine | AgentState TypedDict |
| Agents → Analytics | Async function call | Python dict |
| Agents → ML | Async function call | NumPy arrays / DataFrames |
| Agents → PostgreSQL | Async SQL (asyncpg) | SQL result sets |
| Agents → Neo4j | Async Cypher (neo4j driver) | Graph records |
| Agents → Gemini | LangChain invoke | Messages / Strings |
| Analytics → PostgreSQL | Async SQL | SQL result sets |
| Analytics → Neo4j | Async Cypher | Graph records |

---

## 5. Security Architecture

| Layer | Security Measure | Implementation |
|---|---|---|
| **API** | CORS policy | Restrict origins to frontend domain |
| **API** | Rate limiting | Per-IP request throttling |
| **API** | Input validation | Pydantic model validation on all inputs |
| **Database** | Connection pooling | Bounded pool with timeout |
| **Database** | Parameterized queries | Prevent SQL/Cypher injection |
| **AI** | API key management | Environment variables, never in code |
| **AI** | Output sanitization | Validate LLM outputs before returning |
| **Infrastructure** | Docker isolation | Container-level network isolation |

---

## 6. Scalability Considerations

```mermaid
graph TD
    subgraph HorizontalScaling["Horizontal Scaling"]
        LB[Load Balancer] --> API1[API Instance 1]
        LB --> API2[API Instance 2]
        LB --> API3[API Instance N]
    end

    subgraph VerticalScaling["Vertical Scaling"]
        AsyncIO[Async I/O] --> ConnectionPool[Connection Pooling]
        ConnectionPool --> CacheLayer[Response Caching]
    end

    subgraph DataScaling["Data Scaling"]
        PGReplica[PostgreSQL Read Replicas]
        NeoCluster[Neo4j Clustering]
    end
```

| Concern | Strategy | Implementation |
|---|---|---|
| **API Throughput** | Async handlers + connection pooling | FastAPI + asyncpg |
| **ML Inference** | Model caching + batch prediction | Joblib persistence + batch endpoints |
| **Database Load** | Connection pooling + query optimization | asyncpg pool + indexed queries |
| **AI API Limits** | Rate limiting + request queuing | Custom rate limiter + asyncio.Queue |
| **Memory** | Streaming responses + lazy loading | FastAPI StreamingResponse |

---

## 7. Error Handling Strategy

```mermaid
graph TD
    Error[Error Occurs] --> Classify{Error Type}

    Classify -->|Database Error| DBHandler[DB Error Handler]
    Classify -->|AI API Error| AIHandler[AI Error Handler]
    Classify -->|Validation Error| ValHandler[Validation Handler]
    Classify -->|ML Error| MLHandler[ML Error Handler]
    Classify -->|Unknown| GenHandler[Generic Handler]

    DBHandler --> Retry{Retryable?}
    AIHandler --> Retry
    MLHandler --> Retry

    Retry -->|Yes| RetryLogic[Retry with Backoff]
    Retry -->|No| Fallback[Fallback Response]

    RetryLogic --> Success{Success?}
    Success -->|Yes| Response[Normal Response]
    Success -->|No| Fallback

    ValHandler --> ErrorResponse[400 Error Response]
    Fallback --> ErrorResponse2[500 Error Response]
    GenHandler --> ErrorResponse3[500 Error Response]
```

---

*Sentinel AI Architecture — Built for Intelligence, Designed for Scale*
