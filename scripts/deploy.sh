#!/bin/bash
set -e

# Define variables
PROJECT_ID=${1:-"semantc-ai"}
ENVIRONMENT=${2:-"dev"}
REGION=${3:-"us-central1"}
SERVICE_NAME="vmhub-whatsapp"
IMAGE_NAME="whatsapp-service"

# Validate inputs
if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./deploy.sh <project-id> [environment] [region]"
    echo "Example: ./deploy.sh semantc-ai dev us-central1"
    exit 1
fi

echo "🚀 Starting deployment..."
echo "Project ID: $PROJECT_ID"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"

# Ensure we're in the right directory
cd "$(dirname "$0")/.."

# Set up gcloud configuration
echo "🔧 Configuring gcloud..."
gcloud config set project $PROJECT_ID

# Enable required APIs (if not already enabled)
echo "🔌 Enabling required APIs..."
gcloud services enable \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com

# Create Artifact Registry repository if it doesn't exist
echo "📦 Setting up Artifact Registry..."
gcloud artifacts repositories create $SERVICE_NAME \
    --repository-format=docker \
    --location=$REGION \
    --quiet || true

# Build the image
echo "🏗️ Building Docker image..."
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$IMAGE_NAME:$ENVIRONMENT"

docker build -t $IMAGE_TAG .

# Push to Artifact Registry
echo "📤 Pushing image to Artifact Registry..."
docker push $IMAGE_TAG

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --port 8080 \
    --set-env-vars "ENVIRONMENT=$ENVIRONMENT" \
    --set-env-vars-from-file .env.yaml \
    --allow-unauthenticated

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo "✅ Deployment completed successfully!"
echo "Service URL: $SERVICE_URL"
echo "To test the deployment:"
echo "curl $SERVICE_URL/health"