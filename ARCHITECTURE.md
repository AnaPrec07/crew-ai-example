# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User / Client                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS Request
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Run                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Crew AI Application Container                 │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │           TripCrew Orchestrator                     │  │  │
│  │  │  • Coordinates agents                               │  │  │
│  │  │  • Manages task execution                           │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌─────────┐  │  │
│  │  │ Expert Travel    │  │ City Selection   │  │ Local   │  │  │
│  │  │ Agent            │  │ Expert           │  │ Guide   │  │  │
│  │  │ (Gemini Pro)     │  │ (Gemini Pro)     │  │ (Gemini)│  │  │
│  │  └──────────────────┘  └──────────────────┘  └─────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────────┐  ┌──────────────────┐                │  │
│  │  │ Search Tools     │  │ Calculator Tools │                │  │
│  │  │ (Serper API)     │  │                  │                │  │
│  │  └──────────────────┘  └──────────────────┘                │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Service Account Authentication
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Google Vertex AI                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Gemini Pro Model API                         │  │
│  │  • Natural Language Processing                            │  │
│  │  • Multi-turn conversations                               │  │
│  │  • Reasoning and planning                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  External Services                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Serper API (Internet Search)                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Google Cloud Run
- **Purpose**: Serverless container hosting
- **Features**:
  - Automatic scaling (0 to N instances)
  - Pay-per-use pricing
  - Built-in load balancing
  - HTTPS endpoints
- **Configuration**:
  - CPU: 2 cores
  - Memory: 2GB
  - Max instances: 10
  - Timeout: 300s

### 2. Crew AI Application
- **Language**: Python 3.11
- **Framework**: CrewAI
- **Components**:
  - **TripCrew**: Orchestrates multiple agents
  - **Agents**: Specialized AI workers
    - Expert Travel Agent: Creates detailed itineraries
    - City Selection Expert: Analyzes and recommends cities
    - Local Tour Guide: Provides city-specific insights
  - **Tools**: External integrations
    - Search Tools: Web search via Serper API
    - Calculator Tools: Mathematical operations

### 3. Google Vertex AI
- **Model**: Gemini Pro
- **Purpose**: Large Language Model inference
- **Features**:
  - Multi-modal understanding
  - Context-aware responses
  - High-quality text generation
- **Authentication**: Service Account with `roles/aiplatform.user`

### 4. Service Account
- **Name**: crew-ai-runner
- **Permissions**:
  - `roles/aiplatform.user` - Access Vertex AI
  - `roles/aiplatform.serviceAgent` - Full AI platform access
  - `roles/logging.logWriter` - Write logs
- **Purpose**: Secure, least-privilege authentication

### 5. Artifact Registry
- **Purpose**: Docker image storage
- **Location**: Same region as Cloud Run
- **Repository**: crew-ai-images
- **Format**: Docker

## Data Flow

### Request Processing Flow

```
1. User Request
   ├─> Cloud Run receives HTTP request
   ├─> TripCrew initializes with user input
   │   ├─> Origin city
   │   ├─> Destination cities
   │   ├─> Travel dates
   │   └─> Interests
   │
2. Agent Coordination
   ├─> TripCrew creates agent instances
   ├─> Agents initialized with Gemini Pro LLM
   └─> Tasks assigned to agents
   │
3. Parallel Execution
   ├─> Expert Travel Agent
   │   ├─> Calls Vertex AI API
   │   ├─> Uses search tools (Serper API)
   │   └─> Plans 7-day itinerary
   │
   ├─> City Selection Expert
   │   ├─> Calls Vertex AI API
   │   ├─> Analyzes weather data
   │   └─> Compares destinations
   │
   └─> Local Tour Guide
       ├─> Calls Vertex AI API
       ├─> Gathers local information
       └─> Provides recommendations
   │
4. Result Aggregation
   ├─> Crew collects all agent outputs
   ├─> Combines into final itinerary
   └─> Returns to user
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Run Instance                           │
│  1. Container starts with attached service account              │
│  2. Application Default Credentials (ADC) initialized           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Service Account Token
                         │ (automatically injected)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Google Cloud IAM                                   │
│  3. Validates service account                                   │
│  4. Checks role bindings                                        │
│  5. Issues temporary access token                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Access Token
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Vertex AI API                                │
│  6. Validates token                                             │
│  7. Authorizes API call                                         │
│  8. Returns model response                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Development                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. Code changes committed to GitHub                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Git Push
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Build (Optional CI/CD)                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  2. Trigger on push to main branch                        │  │
│  │  3. Build Docker image                                    │  │
│  │  4. Push to Artifact Registry                             │  │
│  │  5. Deploy to Cloud Run                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Or Manual Deployment
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Terraform                                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Infrastructure as Code                                   │  │
│  │  • Creates service account                                │  │
│  │  • Sets IAM permissions                                   │  │
│  │  • Creates Artifact Registry                              │  │
│  │  • Deploys Cloud Run service                              │  │
│  │  • Configures environment variables                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Security Architecture

### Defense in Depth Layers

1. **Network Security**
   - HTTPS only (TLS 1.2+)
   - Cloud Run ingress controls
   - Optional: VPC Service Controls

2. **Authentication & Authorization**
   - Service Account-based auth
   - IAM role-based access control (RBAC)
   - Least privilege principle
   - Token-based API authentication

3. **Secrets Management**
   - Environment variables for non-sensitive config
   - Google Secret Manager for sensitive data
   - No hardcoded credentials
   - Service account keys never stored in code

4. **Application Security**
   - Container runs as non-root user
   - Minimal base image (Python slim)
   - Dependency vulnerability scanning
   - Regular updates

5. **Monitoring & Logging**
   - Cloud Logging integration
   - Audit logs enabled
   - Cloud Monitoring alerts
   - Error tracking

## Cost Structure

### Variable Costs (Pay-per-use)

1. **Cloud Run**
   - CPU time: $0.00002400 per vCPU-second
   - Memory: $0.00000250 per GiB-second
   - Requests: $0.40 per million requests
   - Free tier: 2 million requests/month

2. **Vertex AI (Gemini Pro)**
   - Input: ~$0.00025 per 1K characters
   - Output: ~$0.0005 per 1K characters
   - Varies by region and model

3. **Artifact Registry**
   - Storage: $0.10 per GB/month
   - Egress: Standard network rates
   - Free tier: 0.5 GB storage

4. **Serper API**
   - Varies by plan
   - Typically $50/month for 5,000 searches

### Fixed Costs
- Minimal when using free tiers and scaling to zero

### Cost Optimization Tips
- Set `min_instances = 0` to scale to zero
- Use caching for repeated queries
- Monitor usage with Cloud Billing
- Set up budget alerts

## Scaling Characteristics

### Horizontal Scaling
- **Min instances**: 0 (scales to zero)
- **Max instances**: 10 (configurable)
- **Scaling metric**: Request concurrency
- **Scale-up time**: ~10 seconds (cold start)
- **Scale-down time**: Gradual, based on traffic

### Vertical Scaling
- **CPU**: 1-8 vCPUs per instance
- **Memory**: 512MB - 32GB per instance
- **Current config**: 2 vCPU, 2GB RAM

### Performance Characteristics
- **Cold start**: 5-15 seconds
- **Warm request**: 100ms - 5s (depending on AI processing)
- **Concurrent requests**: 80 per instance (default)

## Monitoring & Observability

### Key Metrics
1. **Application Metrics**
   - Request count
   - Response time
   - Error rate
   - Agent execution time

2. **Infrastructure Metrics**
   - CPU utilization
   - Memory usage
   - Instance count
   - Cold start frequency

3. **AI Metrics**
   - Vertex AI API calls
   - Token usage
   - Model latency
   - API errors

### Logging
- **Application logs**: stdout/stderr to Cloud Logging
- **Request logs**: Automatic via Cloud Run
- **Audit logs**: IAM and API access
- **Error tracking**: Cloud Error Reporting

## Disaster Recovery

### Backup Strategy
- Code: Version controlled in Git
- Infrastructure: Terraform state
- Configuration: terraform.tfvars (backed up separately)
- No persistent data to backup (stateless)

### Recovery Time Objective (RTO)
- **Regional failure**: Deploy to new region (~15 min)
- **Service deletion**: Terraform apply (~5 min)
- **Bad deployment**: Rollback to previous version (~2 min)

### High Availability
- Multi-zone deployment (automatic with Cloud Run)
- Health checks and auto-restart
- Load balancing across instances
- Regional service availability

## Future Enhancements

### Potential Improvements
1. **Multi-Region Deployment**
   - Deploy to multiple regions
   - Global load balancing
   - Lower latency worldwide

2. **Caching Layer**
   - Redis/Memorystore for repeated queries
   - Reduce API calls and costs

3. **Async Processing**
   - Cloud Tasks for long-running requests
   - Pub/Sub for event-driven architecture

4. **Advanced Monitoring**
   - Custom dashboards
   - Alerting policies
   - SLO/SLI tracking

5. **Enhanced Security**
   - VPC Service Controls
   - Binary Authorization
   - Workload Identity Federation
