# Crew AI Travel Agent - GCP Cloud Run Deployment

A multi-agent travel planning system powered by Google Cloud's Vertex AI and deployed on Cloud Run.

## Overview

This project uses CrewAI to orchestrate multiple AI agents that work together to plan travel itineraries. The agents use Google's Vertex AI (Gemini Pro) for natural language processing and are deployed on Google Cloud Run for scalable serverless execution.

## Architecture

- **AI Platform**: Google Vertex AI (Gemini Pro models)
- **Authentication**: GCP Service Account
- **Deployment**: Google Cloud Run
- **Infrastructure**: Terraform
- **Search**: Serper API for internet searches

## Prerequisites

1. **GCP Account**: Active Google Cloud Platform account
2. **GCP Project**: A GCP project with billing enabled
3. **Tools**:
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.0
   - [Docker](https://docs.docker.com/get-docker/)
   - Python 3.11+

4. **API Keys**:
   - [Serper API Key](https://serper.dev/) for search functionality

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd crew-ai-example
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_LOCATION`: GCP region (default: us-central1)
- `SERPER_API_KEY`: Your Serper API key

### 4. Set Up GCP Authentication

For local development, create a service account and download the key:

```bash
# Create service account
gcloud iam service-accounts create crew-ai-local-dev \
    --display-name="Crew AI Local Development"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:crew-ai-local-dev@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Download key
gcloud iam service-accounts keys create service-account-key.json \
    --iam-account=crew-ai-local-dev@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"
```

### 5. Run Locally

```bash
python main.py
```

## Cloud Deployment

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Configure Terraform Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set your values:
- `project_id`: Your GCP project ID
- `region`: Desired GCP region
- `serper_api_key`: Your Serper API key
- Other optional configuration

### 3. Create Infrastructure

```bash
terraform plan
terraform apply
```

This will create:
- Service account with Vertex AI permissions
- Artifact Registry repository
- Cloud Run service
- Enable required APIs

### 4. Build and Push Docker Image

```bash
# Authenticate Docker with GCP
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push (from project root)
cd ..
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/crew-ai-images/crew-ai:latest
```

### 5. Update Cloud Run Service

Update `terraform.tfvars` with the container image URL:
```hcl
container_image = "us-central1-docker.pkg.dev/YOUR_PROJECT_ID/crew-ai-images/crew-ai:latest"
```

Apply changes:
```bash
cd terraform
terraform apply
```

### 6. Get Service URL

```bash
terraform output cloud_run_service_url
```

## Project Structure

```
.
├── agents.py                 # AI agent definitions
├── tasks.py                  # Task definitions for agents
├── main.py                   # Main application entry point
├── tools/                    # Custom tools for agents
│   ├── search_tools.py      # Internet search tool
│   └── calculator_tools.py  # Calculator tool
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── .env.example             # Environment variables template
└── terraform/               # Infrastructure as Code
    ├── main.tf              # Main Terraform configuration
    ├── variables.tf         # Variable definitions
    ├── outputs.tf           # Output values
    └── terraform.tfvars.example  # Terraform variables template
```

## Agents

The system includes three specialized agents:

1. **Expert Travel Agent**: Creates detailed 7-day itineraries with budget, packing, and safety tips
2. **City Selection Expert**: Analyzes destinations based on weather, events, and costs
3. **Local Tour Guide**: Provides in-depth city information and recommendations

## Configuration

### Environment Variables

- `GCP_PROJECT_ID`: Your GCP project ID (required)
- `GCP_LOCATION`: GCP region for Vertex AI (default: us-central1)
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key (local dev only)
- `SERPER_API_KEY`: API key for Serper search service

### Terraform Variables

See `terraform/variables.tf` for all available configuration options:
- Resource limits (CPU, memory)
- Scaling configuration (min/max instances)
- Access control (authenticated/unauthenticated)
- Service naming

## Security Notes

1. **Service Account**: The application uses a dedicated service account with minimal permissions (Vertex AI User role)
2. **Secrets**: Use Google Secret Manager for production secrets instead of environment variables
3. **Authentication**: By default, Cloud Run requires authentication. Set `allow_unauthenticated = true` only for testing
4. **API Keys**: Never commit API keys or service account keys to version control

## Cost Optimization

- **Cloud Run**: Pay only for requests and CPU time (scales to zero)
- **Vertex AI**: Pay per API call
- **Artifact Registry**: Minimal storage costs for Docker images

Set `min_instances = 0` in Terraform to ensure the service scales to zero when not in use.

## Troubleshooting

### Authentication Errors

```bash
# Check current credentials
gcloud auth list

# Set project
gcloud config set project YOUR_PROJECT_ID

# Re-authenticate
gcloud auth application-default login
```

### Vertex AI API Not Enabled

```bash
gcloud services enable aiplatform.googleapis.com
```

### Container Build Failures

Check Cloud Build logs:
```bash
gcloud builds list
gcloud builds log BUILD_ID
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo Issues URL]
- Documentation: [Additional Docs URL]
