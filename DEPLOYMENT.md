# Deployment Guide

This guide walks you through deploying the Crew AI Travel Agent to Google Cloud Run step by step.

## Prerequisites Checklist

- [ ] GCP account with billing enabled
- [ ] GCP project created
- [ ] gcloud CLI installed and authenticated
- [ ] Terraform installed
- [ ] Docker installed (for local testing)
- [ ] Serper API key obtained

## Quick Start Deployment

### Step 1: Set Up GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable billing (must be done in console if not already enabled)
# Visit: https://console.cloud.google.com/billing
```

### Step 2: Enable Required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

### Step 3: Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd crew-ai-example

# Configure Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

Required values in `terraform.tfvars`:
```hcl
project_id = "your-project-id"
region     = "us-central1"
serper_api_key = "your-serper-api-key"
allow_unauthenticated = true  # For testing; set to false for production
```

### Step 4: Deploy Infrastructure with Terraform

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

This will output:
- Service account email
- Artifact Registry repository URL
- Deployment commands

### Step 5: Build and Deploy Application

```bash
# Go back to project root
cd ..

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push the container image
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/crew-ai-images/crew-ai:latest

# Update terraform.tfvars with the image URL
echo 'container_image = "us-central1-docker.pkg.dev/'$PROJECT_ID'/crew-ai-images/crew-ai:latest"' >> terraform/terraform.tfvars

# Deploy to Cloud Run
cd terraform
terraform apply
```

### Step 6: Test Your Deployment

```bash
# Get the service URL
SERVICE_URL=$(terraform output -raw cloud_run_service_url)
echo "Service URL: $SERVICE_URL"

# If you enabled unauthenticated access, you can curl it:
curl $SERVICE_URL

# For authenticated access:
gcloud run services proxy crew-ai-travel-agent --region us-central1
```

## Using Secret Manager (Recommended for Production)

Instead of passing secrets as environment variables, use Google Secret Manager:

### Create Secret

```bash
# Create secret for Serper API key
echo -n "your-serper-api-key" | gcloud secrets create serper-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Grant service account access to the secret
gcloud secrets add-iam-policy-binding serper-api-key \
  --member="serviceAccount:crew-ai-runner@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Update Cloud Run to Use Secret

```bash
gcloud run services update crew-ai-travel-agent \
  --region us-central1 \
  --set-secrets="SERPER_API_KEY=serper-api-key:latest"
```

## Setting Up CI/CD with Cloud Build

### Connect GitHub Repository

```bash
# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Connect your GitHub repository
gcloud builds connections create github YOUR_CONNECTION_NAME \
  --region=us-central1

# Create a trigger
gcloud builds triggers create github \
  --name="crew-ai-deploy" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --repo-name="crew-ai-example" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --region=us-central1
```

Now every push to the main branch will automatically build and deploy!

## Monitoring and Logs

### View Logs

```bash
# Stream logs from Cloud Run
gcloud run services logs read crew-ai-travel-agent \
  --region us-central1 \
  --limit 50 \
  --follow

# View in Cloud Console
# https://console.cloud.google.com/run
```

### Monitor Costs

```bash
# View billing
gcloud billing accounts list

# Set up budget alerts in Cloud Console:
# https://console.cloud.google.com/billing/budgets
```

## Updating the Application

### Update Code and Redeploy

```bash
# Make your code changes
git add .
git commit -m "Your changes"
git push

# Build new image
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROJECT_ID/crew-ai-images/crew-ai:latest

# Terraform will automatically use the latest tag
cd terraform
terraform apply
```

### Quick Update (without Terraform)

```bash
# Deploy directly with gcloud
gcloud run deploy crew-ai-travel-agent \
  --image us-central1-docker.pkg.dev/$PROJECT_ID/crew-ai-images/crew-ai:latest \
  --region us-central1
```

## Troubleshooting

### Issue: "Permission Denied" Errors

```bash
# Check your authentication
gcloud auth list

# Re-authenticate if needed
gcloud auth login
gcloud auth application-default login
```

### Issue: Container Build Fails

```bash
# Check build logs
gcloud builds list
gcloud builds log [BUILD_ID]

# Test locally
docker build -t crew-ai-test .
docker run -p 8080:8080 crew-ai-test
```

### Issue: Vertex AI Permission Errors

```bash
# Verify service account has correct role
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:crew-ai-runner@$PROJECT_ID.iam.gserviceaccount.com"

# Grant Vertex AI User role if missing
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:crew-ai-runner@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### Issue: Cloud Run Service Not Accessible

```bash
# Check service status
gcloud run services describe crew-ai-travel-agent --region us-central1

# Check IAM policy
gcloud run services get-iam-policy crew-ai-travel-agent --region us-central1

# Allow unauthenticated (testing only)
gcloud run services add-iam-policy-binding crew-ai-travel-agent \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

## Cleanup

To delete all resources and avoid charges:

```bash
cd terraform
terraform destroy

# Confirm with 'yes'
```

This will remove:
- Cloud Run service
- Service account
- Artifact Registry repository
- All IAM bindings

## Cost Estimation

Approximate monthly costs (may vary):
- **Cloud Run**: ~$0 (free tier covers most development usage)
- **Vertex AI API calls**: ~$0.001 - $0.01 per request
- **Artifact Registry**: ~$0.10/GB per month
- **Cloud Build**: First 120 build-minutes/day free

**Estimated total for light usage**: $5-20/month

## Security Best Practices

1. **Never commit secrets**: Use Secret Manager or environment variables
2. **Limit service account permissions**: Follow principle of least privilege
3. **Enable authentication**: Set `allow_unauthenticated = false` in production
4. **Use VPC**: Consider VPC Service Controls for sensitive workloads
5. **Regular updates**: Keep dependencies updated
6. **Audit logs**: Enable Cloud Audit Logs

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [CrewAI Documentation](https://docs.crewai.com/)

## Getting Help

If you encounter issues:
1. Check the logs: `gcloud run services logs read crew-ai-travel-agent --region us-central1`
2. Review the [Troubleshooting](#troubleshooting) section
3. Open an issue in the GitHub repository
4. Consult GCP support or community forums
