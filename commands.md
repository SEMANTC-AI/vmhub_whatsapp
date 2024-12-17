# Set up authentication for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Create repository in Artifact Registry (one-time setup)
gcloud artifacts repositories create vmhub-whatsapp \
    --repository-format=docker \
    --location=us-central1 \
    --description="VMHub WhatsApp Service"

# Build the image
docker build -t vmhub-whatsapp:latest .

# Tag for Artifact Registry
docker tag vmhub-whatsapp:latest us-central1-docker.pkg.dev/[PROJECT-ID]/vmhub-whatsapp/whatsapp-service:latest

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/[PROJECT-ID]/vmhub-whatsapp/whatsapp-service:latest

# Deploy to Cloud Run
gcloud run deploy vmhub-whatsapp \
    --image us-central1-docker.pkg.dev/[PROJECT-ID]/vmhub-whatsapp/whatsapp-service:latest \
    --platform managed \
    --region us-central1 \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --set-env-vars "TWILIO_ACCOUNT_SID=[SID],ENVIRONMENT=production"