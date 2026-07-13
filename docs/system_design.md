# Sentinel AI — System Design Document

## Comprehensive Technical Design Reference

---

## 1. System Design Principles

| Principle | Application |
|---|---|
| **Separation of Concerns** | Each layer (API, agents, ML, analytics, data) has distinct responsibilities |
| **Single Responsibility** | Each module/class handles one specific domain |
| **Open/Closed** | Extensible agent architecture, new agents can be added without modifying orchestrator logic |
| **Dependency Inversion** | Agents depend on abstractions (interfaces), not concrete database implementations |
| **Async-First** | All I/O-bound operations use async/await for non-blocking execution |
| **Fail-Safe** | Graceful degradation with fallback responses when components fail |

---

## 2. Database Design

### 2.1 PostgreSQL Schema Design

```mermaid
erDiagram
    crimes {
        uuid id PK
        varchar crime_type
        text description
        timestamp occurred_at
        timestamp reported_at
        varchar status
        float latitude
        float longitude
        varchar district
        varchar station
        varchar severity
        varchar fir_number
        text modus_operandi
        timestamp created_at
        timestamp updated_at
    }

    suspects {
        uuid id PK
        varchar name
        int age
        varchar gender
        text address
        text description
        varchar risk_level
        text known_aliases
        varchar id_type
        varchar id_number
        timestamp created_at
    }

    officers {
        uuid id PK
        varchar name
        varchar badge_number
        varchar rank
        varchar station
        varchar specialization
        float workload_score
        boolean is_active
        varchar contact
        timestamp created_at
    }

    evidence {
        uuid id PK
        uuid crime_id FK
        varchar evidence_type
        text description
        varchar storage_location
        timestamp collected_at
        varchar collected_by
        varchar chain_of_custody
        varchar status
    }

    crime_suspects {
        uuid id PK
        uuid crime_id FK
        uuid suspect_id FK
        varchar role
        varchar status
        text notes
    }

    officer_assignments {
        uuid id PK
        uuid officer_id FK
        uuid crime_id FK
        varchar assignment_type
        timestamp assigned_at
        timestamp completed_at
        varchar status
    }

    predictions {
        uuid id PK
        varchar prediction_type
        varchar model_version
        jsonb input_params
        jsonb result_data
        float confidence
        timestamp valid_from
        timestamp valid_until
        timestamp generated_at
    }

    reports {
        uuid id PK
        varchar report_type
        varchar title
        jsonb content
        jsonb metadata
        varchar generated_by
        varchar status
        timestamp generated_at
    }

    locations {
        uuid id PK
        varchar name
        varchar location_type
        float latitude
        float longitude
        varchar district
        varchar zone
        jsonb demographics
    }

    simulation_results {
        uuid id PK
        varchar scenario_name
        jsonb parameters
        jsonb results
        jsonb recommendations
        float confidence
        timestamp executed_at
    }

    crimes ||--o{ evidence : "has"
    crimes ||--o{ crime_suspects : "involves"
    suspects ||--o{ crime_suspects : "linked_to"
    officers ||--o{ officer_assignments : "assigned"
    crimes ||--o{ officer_assignments : "has_assignment"
    crimes }o--|| locations : "occurred_at"
```

### 2.2 Key Indexes

```sql
-- Performance-critical indexes
CREATE INDEX idx_crimes_district ON crimes(district);
CREATE INDEX idx_crimes_type ON crimes(crime_type);
CREATE INDEX idx_crimes_occurred_at ON crimes(occurred_at);
CREATE INDEX idx_crimes_status ON crimes(status);
CREATE INDEX idx_crimes_location ON crimes(latitude, longitude);
CREATE INDEX idx_crimes_severity ON crimes(severity);
CREATE INDEX idx_suspects_risk ON suspects(risk_level);
CREATE INDEX idx_officers_station ON officers(station);
CREATE INDEX idx_officers_active ON officers(is_active);
CREATE INDEX idx_predictions_type ON predictions(prediction_type);
CREATE INDEX idx_predictions_generated ON predictions(generated_at);
```

### 2.3 Neo4j Graph Model

```mermaid
graph TD
    subgraph NodeTypes["Node Types"]
        S((Suspect))
        C[Crime]
        L{Location}
        E[Evidence]
        V[Vehicle]
        O((Officer))
        ST[Station]
        G[Gang/Group]
    end

    subgraph Relationships
        S -->|COMMITTED| C
        S -->|ASSOCIATED_WITH| S
        S -->|LIVES_IN| L
        S -->|OWNS| V
        S -->|MEMBER_OF| G
        C -->|OCCURRED_AT| L
        C -->|HAS_EVIDENCE| E
        C -->|SIMILAR_MO| C
        C -->|PRECEDED_BY| C
        O -->|ASSIGNED_TO| C
        O -->|STATIONED_AT| ST
        V -->|SEEN_AT| L
        V -->|USED_IN| C
    end
```

**Node Properties**:

| Node | Key Properties |
|---|---|
| **Suspect** | `id, name, age, gender, risk_level, aliases` |
| **Crime** | `id, type, severity, occurred_at, status, modus_operandi` |
| **Location** | `id, name, latitude, longitude, district, zone` |
| **Evidence** | `id, type, description, status` |
| **Vehicle** | `id, make, model, color, registration` |
| **Officer** | `id, name, badge_number, rank, specialization` |
| **Station** | `id, name, district, zone` |
| **Gang** | `id, name, known_territory, threat_level` |

**Relationship Properties**:

| Relationship | Properties |
|---|---|
| `COMMITTED` | `role, timestamp, confidence` |
| `ASSOCIATED_WITH` | `relationship_type, strength, since` |
| `SIMILAR_MO` | `similarity_score, shared_features` |
| `PRECEDED_BY` | `time_gap, same_suspect` |

### 2.4 Cypher Query Patterns

```cypher
// Find criminal network for a suspect (2 degrees)
MATCH path = (s:Suspect {id: $suspect_id})-[:ASSOCIATED_WITH*1..2]-(connected:Suspect)
RETURN path

// Find crimes with similar modus operandi
MATCH (c1:Crime {id: $crime_id})-[:SIMILAR_MO]-(c2:Crime)
WHERE c2.status = 'open'
RETURN c2, c2.modus_operandi

// Identify crime hotspot locations
MATCH (c:Crime)-[:OCCURRED_AT]->(l:Location)
WHERE c.occurred_at > datetime() - duration('P30D')
WITH l, COUNT(c) as crime_count
WHERE crime_count > 5
RETURN l, crime_count ORDER BY crime_count DESC

// Officer workload analysis
MATCH (o:Officer)-[:ASSIGNED_TO]->(c:Crime)
WHERE c.status = 'open'
WITH o, COUNT(c) as active_cases
RETURN o.name, o.badge_number, active_cases ORDER BY active_cases DESC
```

---

## 3. API Design

### 3.1 Request/Response Schema Design

```mermaid
graph LR
    subgraph Request["Request Flow"]
        Client[Client] -->|JSON Body| Validator[Pydantic Validator]
        Validator -->|Valid| Handler[Route Handler]
        Validator -->|Invalid| Error400[400 Bad Request]
    end

    subgraph Response["Response Flow"]
        Handler -->|Success| Response200[200 OK + JSON]
        Handler -->|Created| Response201[201 Created + JSON]
        Handler -->|Not Found| Response404[404 Not Found]
        Handler -->|Server Error| Response500[500 Internal Error]
    end
```

**Standard Response Envelope**:

```python
{
    "success": True,
    "data": { ... },           # Response payload
    "message": "Operation completed successfully",
    "metadata": {
        "timestamp": "2026-07-13T10:30:00Z",
        "request_id": "uuid",
        "processing_time_ms": 145
    }
}
```

**Standard Error Response**:

```python
{
    "success": False,
    "data": None,
    "message": "Detailed error description",
    "error_code": "CRIME_NOT_FOUND",
    "metadata": {
        "timestamp": "2026-07-13T10:30:00Z",
        "request_id": "uuid"
    }
}
```

### 3.2 Key API Contracts

| Endpoint | Method | Request Body | Response |
|---|---|---|---|
| `/api/crimes` | GET | Query params: `district, type, date_from, date_to, limit` | `CrimeListResponse` |
| `/api/crimes/{id}` | GET | — | `CrimeDetailResponse` |
| `/api/predictions/hotspots` | GET | Query params: `district, days_ahead` | `HotspotPredictionResponse` |
| `/api/predictions/forecast` | GET | Query params: `district, crime_type, horizon` | `ForecastResponse` |
| `/api/chat` | POST | `{ "query": str, "session_id": str }` | `ChatResponse` |
| `/api/reports/generate` | POST | `{ "type": str, "params": dict }` | `ReportResponse` |
| `/api/simulation/run` | POST | `SimulationRequest` | `SimulationResponse` |
| `/api/network/graph` | GET | Query params: `entity_id, depth` | `GraphResponse` |
| `/api/recommendations/officers` | GET | Query params: `zone, crime_type` | `RecommendationResponse` |

---

## 4. Component Communication Design

### 4.1 Inter-Module Communication

```mermaid
graph TD
    subgraph API["API Layer"]
        Routes[Route Handlers]
    end

    subgraph Agents["Agent Layer"]
        Orch[Orchestrator]
        IA[Investigation]
        AA[Analytics]
        PA[Prediction]
        GA[Graph]
        RA[Recommendation]
        RepA[Report]
        SA[Simulation]
    end

    subgraph Analytics["Analytics Layer"]
        CS[Crime Stats]
        TA[Trend Analysis]
        HA[Hotspot Analysis]
        DA[District Analysis]
        CP[Crime Pattern]
        RS[Risk Score]
        RG[Report Gen]
    end

    subgraph ML["ML Layer"]
        HP[Hotspot Prediction]
        CF[Crime Forecasting]
        AD[Anomaly Detection]
        RM[Recommender]
    end

    subgraph Data["Data Layer"]
        PGC[PostgreSQL Client]
        NeoC[Neo4j Client]
    end

    Routes -->|async| Orch
    Routes -->|async| CS
    Routes -->|async| TA

    Orch -->|state| IA
    Orch -->|state| AA
    Orch -->|state| PA
    Orch -->|state| GA
    Orch -->|state| RA
    Orch -->|state| RepA
    Orch -->|state| SA

    AA -->|call| CS
    AA -->|call| TA
    PA -->|call| HP
    PA -->|call| CF
    PA -->|call| AD
    RA -->|call| RM
    GA -->|query| NeoC
    IA -->|query| PGC
    IA -->|query| NeoC

    CS -->|query| PGC
    TA -->|query| PGC
    HA -->|query| PGC
    DA -->|query| PGC
    CP -->|query| NeoC
    RS -->|call| CS
    RS -->|call| TA
    HP -->|query| PGC
    CF -->|query| PGC
```

### 4.2 Communication Patterns

| Pattern | Used Between | How It Works |
|---|---|---|
| **Async Function Call** | API → Agents, Agents → Analytics | Direct `await` on async methods |
| **LangGraph State** | Orchestrator → Specialist Agents | Shared TypedDict flows through state graph |
| **SQL Query** | Analytics/ML → PostgreSQL | Parameterized SQL via asyncpg |
| **Cypher Query** | Graph Agent/Analytics → Neo4j | Parameterized Cypher via neo4j driver |
| **LLM Invocation** | Agents → Gemini | LangChain `ainvoke` with prompt templates |

---

## 5. ML System Design

### 5.1 Model Registry

```mermaid
graph TD
    subgraph ModelRegistry["Model Registry (File System)"]
        subgraph HotspotModels["Hotspot Models"]
            HM1[hotspot_rf_v1.joblib]
            HM2[hotspot_gb_v1.joblib]
            HM3[hotspot_scaler_v1.joblib]
        end

        subgraph ForecastModels["Forecast Models"]
            FM1[forecast_ridge_v1.joblib]
            FM2[forecast_scaler_v1.joblib]
        end

        subgraph AnomalyModels["Anomaly Models"]
            AM1[anomaly_iforest_v1.joblib]
            AM2[anomaly_scaler_v1.joblib]
        end

        subgraph RecommenderModels["Recommender"]
            RM1[recommender_config_v1.json]
        end
    end

    Train[Training Pipeline] -->|saves| ModelRegistry
    ModelRegistry -->|loads| Inference[Inference Pipeline]
```

### 5.2 Feature Store Design

| Feature Category | Features | Source |
|---|---|---|
| **Temporal** | `hour_of_day, day_of_week, month, is_weekend, is_holiday, season` | Crime timestamp |
| **Spatial** | `latitude, longitude, grid_x, grid_y, district_encoded` | Crime location |
| **Historical** | `crimes_last_7d, crimes_last_30d, avg_crimes_per_day, trend_slope` | Aggregated crime data |
| **Demographic** | `population_density, income_level, commercial_density` | Location demographics |
| **Crime-Specific** | `crime_type_encoded, severity_encoded, repeat_offender_count` | Crime records |

### 5.3 Model Evaluation Framework

```mermaid
graph LR
    subgraph Classification["Classification Metrics"]
        Acc[Accuracy]
        Prec[Precision]
        Rec[Recall]
        F1[F1 Score]
        AUC[ROC-AUC]
    end

    subgraph Regression["Regression Metrics"]
        MAE[MAE]
        RMSE[RMSE]
        MAPE[MAPE]
        R2[R² Score]
    end

    subgraph Anomaly["Anomaly Metrics"]
        APrec[Precision]
        ARec[Recall]
        AF1[F1 Score]
        FPR[False Positive Rate]
    end

    Hotspot[Hotspot Model] --> Classification
    Forecast[Forecast Model] --> Regression
    AnomalyModel[Anomaly Model] --> Anomaly
```

---

## 6. Caching Strategy

| Cache Target | TTL | Strategy | Invalidation |
|---|---|---|---|
| Crime statistics | 5 minutes | In-memory dict | Time-based expiry |
| ML predictions | 1 hour | File-based | New prediction overwrites |
| Graph queries | 10 minutes | In-memory dict | Time-based expiry |
| Analytics results | 15 minutes | In-memory dict | Time-based expiry |
| Report templates | 24 hours | File-based | Manual refresh |

---

## 7. Error Handling Design

### 7.1 Exception Hierarchy

```mermaid
graph TD
    BaseError[SentinelBaseError]
    BaseError --> DatabaseError[DatabaseError]
    BaseError --> AIError[AIServiceError]
    BaseError --> MLError[MLModelError]
    BaseError --> ValidationError[ValidationError]
    BaseError --> AuthError[AuthenticationError]

    DatabaseError --> PGError[PostgreSQLError]
    DatabaseError --> NeoError[Neo4jError]
    AIError --> GeminiError[GeminiAPIError]
    AIError --> RateLimitError[RateLimitError]
    MLError --> TrainingError[TrainingError]
    MLError --> InferenceError[InferenceError]
```

### 7.2 Error Recovery Strategies

| Error Type | Recovery Strategy | Fallback |
|---|---|---|
| PostgreSQL connection timeout | Retry 3x with exponential backoff | Return cached data |
| Neo4j connection failure | Retry 2x, then skip graph enrichment | Partial response without graph data |
| Gemini API rate limit | Queue request, retry after delay | Return data without AI narrative |
| Gemini API timeout | Retry 2x with shorter prompts | Structured data only |
| ML model load failure | Re-download from model registry | Return historical predictions |
| Invalid input data | Return 400 with validation details | No fallback needed |

---

## 8. Logging & Monitoring Design

### 8.1 Log Levels

| Level | Usage |
|---|---|
| **DEBUG** | Detailed state changes, query parameters, intermediate results |
| **INFO** | Request processing, agent execution, model loading |
| **WARNING** | Degraded performance, fallback activation, approaching limits |
| **ERROR** | Failed operations, exception details, data integrity issues |
| **CRITICAL** | System-level failures, database unavailable, API key invalid |

### 8.2 Structured Log Format

```json
{
    "timestamp": "2026-07-13T10:30:00Z",
    "level": "INFO",
    "module": "investigation_agent",
    "function": "analyze_evidence",
    "message": "Evidence analysis completed",
    "request_id": "uuid",
    "duration_ms": 234,
    "metadata": {
        "case_id": "uuid",
        "evidence_count": 5,
        "model_used": "gemini-2.0-flash"
    }
}
```

---

## 9. Deployment Design

```mermaid
graph TB
    subgraph DockerCompose["Docker Compose Stack"]
        subgraph FrontendService["frontend"]
            NextJS[Next.js :3000]
        end

        subgraph BackendService["backend"]
            FastAPI[FastAPI :8000]
            Workers[Uvicorn Workers x4]
        end

        subgraph PostgresService["postgres"]
            PG[(PostgreSQL :5432)]
            PGData[Volume: pg_data]
        end

        subgraph Neo4jService["neo4j"]
            Neo[(Neo4j :7474/7687)]
            NeoData[Volume: neo4j_data]
        end
    end

    subgraph External["External Services"]
        GeminiAPI[Gemini API Cloud]
    end

    NextJS -->|"http://backend:8000"| FastAPI
    FastAPI -->|"postgresql://postgres:5432"| PG
    FastAPI -->|"bolt://neo4j:7687"| Neo
    FastAPI -->|"https://generativelanguage.googleapis.com"| GeminiAPI
    PG --- PGData
    Neo --- NeoData
```

**Docker Compose Configuration**:

```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on: [backend]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://sentinel:password@postgres:5432/sentinel_db
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    depends_on: [postgres, neo4j]

  postgres:
    image: postgres:15
    ports: ["5432:5432"]
    environment:
      - POSTGRES_DB=sentinel_db
      - POSTGRES_USER=sentinel
      - POSTGRES_PASSWORD=password
    volumes: [pg_data:/var/lib/postgresql/data]

  neo4j:
    image: neo4j:5
    ports: ["7474:7474", "7687:7687"]
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes: [neo4j_data:/data]

volumes:
  pg_data:
  neo4j_data:
```

---

## 10. Performance Targets

| Metric | Target | Measurement |
|---|---|---|
| API response time (p95) | < 500ms | Route handler execution |
| AI agent response time | < 5s | Full agent pipeline |
| ML inference time | < 200ms | Single prediction |
| Database query time (p95) | < 100ms | PostgreSQL queries |
| Graph query time (p95) | < 200ms | Neo4j traversals |
| Report generation | < 10s | Full report pipeline |
| Concurrent users | 50+ | Load testing |

---

*Sentinel AI System Design — Engineering Excellence for Public Safety*
