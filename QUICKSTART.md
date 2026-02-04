# Quick Start Guide

Get the Crew AI Travel Agent running on Google Cloud Run in under 10 minutes!

## Prerequisites

- Google Cloud account with billing enabled
- [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed
- [Terraform](https://developer.hashicorp.com/terraform/downloads) installed
- [Serper API key](https://serper.dev/) (for search functionality)

## 5-Minute Deployment

### 1. Run Setup Script

```bash
./setup.sh
```

This will:
- Configure your GCP project
- Enable required APIs
- Create configuration files

### 2. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform apply
```

Type `yes` when prompted.

### 3. Build and Deploy

```bash
cd ..
gcloud builds submit --tag $(terraform -chdir=terraform output -raw docker_repository_url)/crew-ai:latest

cd terraform
terraform apply -var="container_image=$(terraform output -raw docker_repository_url)/crew-ai:latest"
```

### 4. Get Your URL

```bash
terraform output cloud_run_service_url
```

✅ **Done!** Your AI travel agent is live!

## Manual Setup (Alternative)

### Step 1: Configure GCP

```bash
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### Step 2: Create Configuration

```bash
# Copy example files
cp .env.example .env
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

# Edit with your values
nano .env
nano terraform/terraform.tfvars
```

### Step 3: Deploy with Terraform

```bash
cd terraform
terraform init
terraform apply
```

### Step 4: Build Container

```bash
cd ..
gcloud auth configure-docker us-central1-docker.pkg.dev
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/crew-ai-images/crew-ai:latest
```

### Step 5: Update and Deploy

```bash
cd terraform
# Add to terraform.tfvars:
# container_image = "us-central1-docker.pkg.dev/PROJECT_ID/crew-ai-images/crew-ai:latest"

terraform apply
```

## Test Your Deployment

### Authenticated Request

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  $(terraform -chdir=terraform output -raw cloud_run_service_url)
```

### Unauthenticated (if enabled)

```bash
curl $(terraform -chdir=terraform output -raw cloud_run_service_url)
```

## Local Development

### 1. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Authentication

```bash
# Create service account for local dev
gcloud iam service-accounts create crew-ai-local \
  --display-name="Crew AI Local Dev"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:crew-ai-local@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Download key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=crew-ai-local@$PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/service-account-key.json"
```

### 3. Run Locally

```bash
python main.py
```

## Common Commands

### View Logs

```bash
gcloud run services logs read crew-ai-travel-agent --region us-central1 --limit 50
```

### Update Application

```bash
# After code changes
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/crew-ai-images/crew-ai:latest
cd terraform && terraform apply
```

### Scale Up/Down

```bash
# Edit terraform/terraform.tfvars
# min_instances = 1  # Keep warm
# max_instances = 20 # Allow more scale

cd terraform
terraform apply
```

### Delete Everything

```bash
cd terraform
terraform destroy
```

## Cost Control

### Keep Costs Low

1. **Scale to Zero**: Set `min_instances = 0`
2. **Monitor Usage**: Check [Cloud Console Billing](https://console.cloud.google.com/billing)
3. **Set Budget Alerts**: 
   ```bash
   # Set up in Cloud Console at:
   # https://console.cloud.google.com/billing/budgets
   ```

### Free Tier Limits

- Cloud Run: 2 million requests/month
- Vertex AI: Limited free credits
- Artifact Registry: 0.5 GB storage

## Troubleshooting

### "Permission Denied"

```bash
gcloud auth login
gcloud auth application-default login
```

### "API Not Enabled"

```bash
gcloud services list --available | grep -i vertex
gcloud services enable aiplatform.googleapis.com
```

### "Container Build Failed"

```bash
# Check logs
gcloud builds list
gcloud builds log [BUILD_ID]
```

### "Service Account Not Found"

```bash
# Re-run terraform
cd terraform
terraform destroy
terraform apply
```

## Next Steps

- 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- 🚀 Read [DEPLOYMENT.md](DEPLOYMENT.md) for advanced deployment
- 📝 Read [README.md](README.md) for detailed documentation
- 🔧 Customize agents in `agents.py`
- 📋 Modify tasks in `tasks.py`

## Getting Help

- Check logs: `gcloud run services logs read crew-ai-travel-agent --region us-central1`
- View service: `gcloud run services describe crew-ai-travel-agent --region us-central1`
- GitHub Issues: [Report a problem](https://github.com/AnaPrec07/crew-ai-example/issues)

## Quick Reference

| Command | Description |
|---------|-------------|
| `./setup.sh` | Initial setup |
| `terraform apply` | Deploy infrastructure |
| `gcloud builds submit` | Build container |
| `terraform output` | Show outputs |
| `terraform destroy` | Delete everything |
| `gcloud run services logs read` | View logs |

---

**Time to First Deploy**: 5-10 minutes  
**Cost**: ~$5-20/month (light usage)  
**Support**: GitHub Issues
