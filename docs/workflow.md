# Sentinel AI — Workflow Documentation

## End-to-End Workflow Reference

---

## 1. System Workflow Overview

Sentinel AI operates through six primary workflows that cover the complete spectrum of crime intelligence operations.

```mermaid
graph TD
    subgraph Workflows["🔄 Sentinel AI Workflows"]
        W1[1. Crime Investigation Workflow]
        W2[2. Predictive Analysis Workflow]
        W3[3. Real-Time Analytics Workflow]
        W4[4. Resource Optimization Workflow]
        W5[5. Report Generation Workflow]
        W6[6. Crime Simulation Workflow]
    end

    User((👤 User)) --> W1
    User --> W2
    User --> W3
    User --> W4
    User --> W5
    User --> W6

    W1 --> Output1[Investigation Reports]
    W2 --> Output2[Predictions & Alerts]
    W3 --> Output3[Live Dashboards]
    W4 --> Output4[Deployment Plans]
    W5 --> Output5[PDF Reports]
    W6 --> Output6[Scenario Analysis]
```

---

## 2. Crime Investigation Workflow

### 2.1 Flow Overview

This workflow handles end-to-end automated crime investigation, from initial case intake to final investigation report generation.

```mermaid
sequenceDiagram
    participant Officer as 👮 Officer
    participant FE as 🖥️ Frontend
    participant API as ⚡ FastAPI
    participant Orch as 🎯 Orchestrator
    participant InvAgent as 🔍 Investigation Agent
    participant GraphAgent as 🔗 Graph Agent
    participant PG as 🗄️ PostgreSQL
    participant Neo as 📊 Neo4j
    participant Gemini as 🌟 Gemini API
    participant ReportAgent as 📄 Report Agent

    Officer->>FE: Submit investigation query
    FE->>API: POST /api/chat {query, context}
    API->>Orch: Route to orchestrator

    Note over Orch: Intent Classification
    Orch->>Orch: Classify as "investigation"

    Orch->>InvAgent: Delegate investigation task

    Note over InvAgent: Step 1 - Case Intake
    InvAgent->>PG: Query crime records
    PG-->>InvAgent: Crime data + evidence

    Note over InvAgent: Step 2 - Evidence Analysis
    InvAgent->>Gemini: Analyze evidence patterns
    Gemini-->>InvAgent: Evidence insights

    Note over InvAgent: Step 3 - Suspect Profiling
    InvAgent->>Neo: Query suspect networks
    Neo-->>InvAgent: Suspect relationships

    Orch->>GraphAgent: Parallel - Network analysis
    GraphAgent->>Neo: Traverse criminal network
    Neo-->>GraphAgent: Network graph

    Note over InvAgent: Step 4 - Timeline Reconstruction
    InvAgent->>Gemini: Build crime timeline
    Gemini-->>InvAgent: Reconstructed timeline

    Note over InvAgent: Step 5 - Conclusion
    InvAgent->>Gemini: Generate investigation summary
    Gemini-->>InvAgent: Investigation conclusion

    InvAgent-->>Orch: Investigation results
    GraphAgent-->>Orch: Network analysis results

    Orch->>ReportAgent: Generate investigation report
    ReportAgent->>Gemini: Compile narrative report
    Gemini-->>ReportAgent: Formatted report
    ReportAgent-->>Orch: Final report

    Orch-->>API: Aggregated response
    API-->>FE: JSON response
    FE-->>Officer: Display investigation results
```

### 2.2 Data Flow

| Step | Source | Processing | Destination |
|---|---|---|---|
| Case Intake | PostgreSQL | SQL query for crime + evidence | Investigation Agent |
| Evidence Analysis | Agent state | Gemini prompt with evidence context | Agent state (insights) |
| Suspect Profiling | Neo4j | Cypher query for relationships | Agent state (suspects) |
| Network Analysis | Neo4j | Graph traversal + community detection | Graph Agent results |
| Timeline | Agent state | Gemini chronological reconstruction | Agent state (timeline) |
| Conclusion | All results | Gemini synthesis of findings | Final report |

---

## 3. Predictive Analysis Workflow

### 3.1 Flow Overview

This workflow generates crime predictions using ML models and enriches them with AI-powered risk assessment.

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚡ FastAPI
    participant Orch as 🎯 Orchestrator
    participant PredAgent as 🔮 Prediction Agent
    participant HotspotML as 🧠 Hotspot Model
    participant ForecastML as 📈 Forecast Model
    participant AnomalyML as ⚠️ Anomaly Model
    participant PG as 🗄️ PostgreSQL
    participant Gemini as 🌟 Gemini API

    User->>FE: Request predictions
    FE->>API: GET /api/predictions/hotspots
    API->>Orch: Route to prediction system

    Orch->>PredAgent: Delegate prediction task

    Note over PredAgent: Step 1 - Data Preparation
    PredAgent->>PG: Fetch historical crime data
    PG-->>PredAgent: Crime dataset

    Note over PredAgent: Step 2 - Model Execution
    par Parallel ML Execution
        PredAgent->>HotspotML: Run hotspot prediction
        HotspotML-->>PredAgent: Hotspot map
    and
        PredAgent->>ForecastML: Run crime forecast
        ForecastML-->>PredAgent: Forecast results
    and
        PredAgent->>AnomalyML: Run anomaly detection
        AnomalyML-->>PredAgent: Anomaly alerts
    end

    Note over PredAgent: Step 3 - Risk Assessment
    PredAgent->>Gemini: Contextualize predictions
    Gemini-->>PredAgent: Risk analysis narrative

    Note over PredAgent: Step 4 - Alert Generation
    PredAgent->>PredAgent: Generate priority alerts
    PredAgent->>PG: Store predictions

    PredAgent-->>Orch: Prediction results
    Orch-->>API: Response
    API-->>FE: Prediction data + maps
    FE-->>User: Interactive prediction dashboard
```

### 3.2 ML Model Pipeline

```mermaid
graph LR
    subgraph Offline["⚙️ Offline Training"]
        RawData[Raw Crime Data] --> Preprocess[Preprocessing]
        Preprocess --> FeatureEng[Feature Engineering]
        FeatureEng --> Split[Train/Test Split]
        Split --> Train[Model Training]
        Train --> Evaluate[Evaluate Metrics]
        Evaluate --> Save[Save Model .joblib]
    end

    subgraph Online["🔄 Online Inference"]
        NewData[New Crime Data] --> PrepInf[Preprocess]
        PrepInf --> FeatInf[Extract Features]
        FeatInf --> Load[Load Model]
        Save -.->|Model File| Load
        Load --> Predict[Generate Predictions]
        Predict --> PostProc[Post-Process]
        PostProc --> Serve[Serve via API]
    end
```

---

## 4. Real-Time Analytics Workflow

### 4.1 Flow Overview

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚡ FastAPI
    participant Orch as 🎯 Orchestrator
    participant AnalAgent as 📊 Analytics Agent
    participant StatsMod as 📐 Statistics Module
    participant TrendMod as 📈 Trend Module
    participant HotMod as 🔥 Hotspot Module
    participant DistMod as 🏘️ District Module
    participant PG as 🗄️ PostgreSQL
    participant Neo as 📊 Neo4j
    participant Gemini as 🌟 Gemini API

    User->>FE: Navigate to analytics dashboard
    FE->>API: GET /api/analytics?district=X&period=30d

    par Analytics Module Calls
        API->>StatsMod: Get crime statistics
        StatsMod->>PG: SQL aggregate queries
        PG-->>StatsMod: Statistical results
    and
        API->>TrendMod: Get trend analysis
        TrendMod->>PG: Time-series queries
        PG-->>TrendMod: Trend data
    and
        API->>HotMod: Get hotspot analysis
        HotMod->>PG: Spatial queries
        PG-->>HotMod: Hotspot clusters
    and
        API->>DistMod: Get district metrics
        DistMod->>PG: District aggregate queries
        PG-->>DistMod: District stats
    end

    API->>Orch: Request AI insights
    Orch->>AnalAgent: Analyze results
    AnalAgent->>Gemini: Generate narrative insights
    Gemini-->>AnalAgent: AI-powered insights
    AnalAgent-->>Orch: Enriched analytics

    Orch-->>API: Complete analytics response
    API-->>FE: JSON analytics data
    FE-->>User: Interactive dashboard with charts
```

### 4.2 Analytics Module Interactions

```mermaid
graph TD
    subgraph Input["📥 Data Sources"]
        PG[(PostgreSQL)]
        Neo[(Neo4j)]
    end

    subgraph Processing["⚙️ Analytics Pipeline"]
        CS[Crime Statistics]
        TA[Trend Analysis]
        HA[Hotspot Analysis]
        DA[District Analysis]
        CP[Crime Patterns]
        RS[Risk Scoring]
    end

    subgraph Output["📤 Output"]
        RG[Report Generator]
        API[API Response]
        Agent[Analytics Agent]
    end

    PG --> CS
    PG --> TA
    PG --> HA
    PG --> DA
    Neo --> CP
    Neo --> HA

    CS --> RS
    TA --> RS
    HA --> RS
    DA --> RS
    CP --> RS

    CS --> RG
    TA --> RG
    HA --> RG
    DA --> RG
    CP --> RG
    RS --> RG

    CS --> API
    TA --> API
    HA --> API
    RS --> Agent
    RG --> Agent
```

---

## 5. Resource Optimization Workflow

### 5.1 Flow Overview

```mermaid
sequenceDiagram
    participant Commander as 👮 Commander
    participant FE as 🖥️ Frontend
    participant API as ⚡ FastAPI
    participant Orch as 🎯 Orchestrator
    participant RecAgent as 💡 Recommendation Agent
    participant RecModel as 🧠 Recommender Model
    participant ScoringEng as 📊 Scoring Engine
    participant PredAgent as 🔮 Prediction Agent
    participant PG as 🗄️ PostgreSQL
    participant Gemini as 🌟 Gemini API

    Commander->>FE: Request officer deployment plan
    FE->>API: POST /api/recommendations/officers

    API->>Orch: Route to recommendation system
    Orch->>RecAgent: Delegate recommendation task

    Note over RecAgent: Step 1 - Context Analysis
    RecAgent->>PG: Fetch officer data + current assignments
    PG-->>RecAgent: Officer profiles + workloads
    RecAgent->>PredAgent: Get current risk predictions
    PredAgent-->>RecAgent: Hotspot risk scores

    Note over RecAgent: Step 2 - Resource Evaluation
    RecAgent->>ScoringEng: Score officer-to-area matches
    ScoringEng->>ScoringEng: Multi-criteria scoring
    ScoringEng-->>RecAgent: Scored assignments

    Note over RecAgent: Step 3 - Strategy Formulation
    RecAgent->>RecModel: Optimize assignments
    RecModel-->>RecAgent: Optimal deployment plan

    Note over RecAgent: Step 4 - AI Enhancement
    RecAgent->>Gemini: Generate deployment rationale
    Gemini-->>RecAgent: Contextual justification

    RecAgent-->>Orch: Recommendations
    Orch-->>API: Deployment plan
    API-->>FE: Officer assignments + map
    FE-->>Commander: Interactive deployment view
```

### 5.2 Scoring Criteria

```mermaid
graph LR
    subgraph Criteria["📋 Scoring Criteria"]
        Risk[Area Risk Score]
        Proximity[Officer Proximity]
        Workload[Current Workload]
        Expertise[Crime Type Expertise]
        History[Past Performance]
    end

    subgraph Weights["⚖️ Weighted Scoring"]
        W1["Risk: 0.30"]
        W2["Proximity: 0.20"]
        W3["Workload: 0.20"]
        W4["Expertise: 0.20"]
        W5["History: 0.10"]
    end

    subgraph Output["📤 Output"]
        Score[Composite Score]
        Rank[Priority Ranking]
        Assign[Assignment Plan]
    end

    Risk --> W1 --> Score
    Proximity --> W2 --> Score
    Workload --> W3 --> Score
    Expertise --> W4 --> Score
    History --> W5 --> Score
    Score --> Rank --> Assign
```

---

## 6. Report Generation Workflow

### 6.1 Flow Overview

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚡ FastAPI
    participant Orch as 🎯 Orchestrator
    participant ReportAgent as 📄 Report Agent
    participant AnalAgent as 📊 Analytics Agent
    participant PredAgent as 🔮 Prediction Agent
    participant RecAgent as 💡 Recommendation Agent
    participant PG as 🗄️ PostgreSQL
    participant Gemini as 🌟 Gemini API

    User->>FE: Request monthly crime report
    FE->>API: POST /api/reports/generate {type: "monthly"}

    API->>Orch: Route to report system
    Orch->>ReportAgent: Initiate report generation

    Note over ReportAgent: Step 1 - Data Aggregation
    par Parallel Data Collection
        ReportAgent->>AnalAgent: Get analytics summary
        AnalAgent-->>ReportAgent: Statistics + trends
    and
        ReportAgent->>PredAgent: Get prediction summary
        PredAgent-->>ReportAgent: Predictions + risks
    and
        ReportAgent->>RecAgent: Get recommendation summary
        RecAgent-->>ReportAgent: Resource insights
    end

    Note over ReportAgent: Step 2 - Report Structuring
    ReportAgent->>ReportAgent: Organize data by sections

    Note over ReportAgent: Step 3 - Narrative Generation
    ReportAgent->>Gemini: Generate executive summary
    Gemini-->>ReportAgent: AI-written narrative
    ReportAgent->>Gemini: Generate section analysis
    Gemini-->>ReportAgent: Section narratives

    Note over ReportAgent: Step 4 - Compilation
    ReportAgent->>ReportAgent: Assemble final report
    ReportAgent->>PG: Store report

    ReportAgent-->>Orch: Complete report
    Orch-->>API: Report data
    API-->>FE: Report JSON + PDF link
    FE-->>User: Display formatted report
```

---

## 7. Crime Simulation Workflow

### 7.1 Flow Overview

```mermaid
sequenceDiagram
    participant Analyst as 👤 Analyst
    participant FE as 🖥️ Frontend
    participant API as ⚡ FastAPI
    participant Orch as 🎯 Orchestrator
    participant SimAgent as 🎮 Simulation Agent
    participant PredAgent as 🔮 Prediction Agent
    participant HotspotML as 🧠 Hotspot Model
    participant PG as 🗄️ PostgreSQL
    participant Gemini as 🌟 Gemini API

    Analyst->>FE: Define simulation scenario
    Note over FE: "What if we add 10 officers to Zone A?"
    FE->>API: POST /api/simulation/run {scenario}

    API->>Orch: Route to simulation system
    Orch->>SimAgent: Execute simulation

    Note over SimAgent: Step 1 - Scenario Definition
    SimAgent->>SimAgent: Parse scenario parameters
    SimAgent->>PG: Fetch baseline data
    PG-->>SimAgent: Current crime + resource data

    Note over SimAgent: Step 2 - Parameter Configuration
    SimAgent->>SimAgent: Configure simulation variables
    SimAgent->>PredAgent: Get baseline predictions
    PredAgent->>HotspotML: Baseline hotspot prediction
    HotspotML-->>PredAgent: Baseline risk map
    PredAgent-->>SimAgent: Baseline predictions

    Note over SimAgent: Step 3 - Simulation Execution
    loop Monte Carlo Iterations (N=100)
        SimAgent->>SimAgent: Run iteration
        SimAgent->>SimAgent: Apply random variation
        SimAgent->>SimAgent: Compute outcome metrics
    end

    Note over SimAgent: Step 4 - Outcome Analysis
    SimAgent->>SimAgent: Aggregate iteration results
    SimAgent->>Gemini: Interpret simulation outcomes
    Gemini-->>SimAgent: Strategic analysis

    Note over SimAgent: Step 5 - Recommendations
    SimAgent->>Gemini: Generate action recommendations
    Gemini-->>SimAgent: Strategic recommendations

    SimAgent-->>Orch: Simulation results
    Orch-->>API: Complete analysis
    API-->>FE: Simulation data + visualizations
    FE-->>Analyst: Interactive results dashboard
```

### 7.2 Simulation Parameters

| Parameter | Type | Description | Example |
|---|---|---|---|
| `officer_delta` | int | Change in officer count per zone | +10, -5 |
| `patrol_frequency` | float | Patrol frequency multiplier | 1.5x |
| `target_zones` | list | Zones affected by change | ["Zone A", "Zone B"] |
| `duration_days` | int | Simulation time horizon | 30, 90, 180 |
| `crime_types` | list | Crime types to simulate | ["theft", "assault"] |
| `confidence_level` | float | Statistical confidence | 0.95 |
| `iterations` | int | Monte Carlo iterations | 100, 500, 1000 |

---

## 8. Cross-Workflow Integration

```mermaid
graph TD
    subgraph Trigger["Workflow Triggers"]
        UserAction[User Action]
        Scheduled[Scheduled Task]
        Alert[System Alert]
    end

    subgraph Workflows
        Investigation[Investigation]
        Prediction[Prediction]
        Analytics[Analytics]
        Recommendation[Recommendation]
        Report[Report]
        Simulation[Simulation]
    end

    subgraph SharedState["Shared State"]
        AgentState[Agent State]
        DB[(Databases)]
        Cache[Result Cache]
    end

    UserAction --> Investigation
    UserAction --> Prediction
    UserAction --> Analytics
    UserAction --> Simulation
    Scheduled --> Prediction
    Scheduled --> Report
    Alert --> Investigation
    Alert --> Recommendation

    Investigation --> AgentState
    Prediction --> AgentState
    Analytics --> AgentState
    Recommendation --> AgentState

    Investigation -.->|feeds into| Report
    Prediction -.->|feeds into| Recommendation
    Analytics -.->|feeds into| Report
    Simulation -.->|validates| Recommendation

    AgentState --> DB
    AgentState --> Cache
```

**Workflow Dependencies**:

| Workflow | Depends On | Feeds Into |
|---|---|---|
| Investigation | Graph Agent, PostgreSQL, Neo4j | Report Generation |
| Prediction | ML Models, Historical Data | Recommendation, Simulation |
| Analytics | PostgreSQL, Neo4j | Report, Recommendation |
| Recommendation | Prediction, Analytics | Simulation (validation) |
| Report | All other workflows | User consumption |
| Simulation | Prediction, Historical Data | Recommendation |

---

*Sentinel AI Workflows — From Data to Decision*
