# Usefull Commands Related to the project

## Backend

### Docker
- To build the docker image: `docker build -t genvid-backend:latest .`
- To run the docker container: `docker run -d -p 8000:8000 --name genvid-backend genvid-backend:latest`


### GCP

### Service Account
```bash
    gcloud iam service-accounts create SERVICE_ACCOUNT_NAME \
        --description="DESCRIPTION" \
        --display-name="DISPLAY_NAME"
``` 

### List Service Accounts
```bash
    gcloud iam service-accounts list
```

### Grant Access to the Service Account
```bash
    gcloud projects add-iam-policy-binding PROJECT_ID \
        --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
        --role="ROLE"
```

Example:
```bash
    gcloud projects add-iam-policy-binding genvidgcp \
    --member="serviceAccount:genvid-cloudrun-sa@genvidgcp.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"
```

#### Create a Artificats Repository
```bash
    gcloud artifacts repositories create REPOSITORY \
        --repository-format=docker \
        --location=LOCATION \
        --description="DESCRIPTION" \
        --immutable-tags \
        --async
```

Example:
```bash
    gcloud artifacts repositories create genvid-artifact-repo \
        --repository-format=docker \
        --location=us-central1 \
        --description="Gen Vid Docker Repository" \
        --immutable-tags \
        --async
```

### Configure Docker to get access to the Artifact Registry
```bash
    gcloud auth configure-docker LOCATION-docker.pkg.dev
```

Example:
```bash
    gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Build the Docker image and push it to the Artifact Registry
```bash
    docker build -t LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG .
    docker push LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG
```

#### For Apple Silicon
```bash
    docker buildx create --use
    docker buildx build --platform linux/amd64 -t LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG --push .
``` 





Example:
```bash
    docker build -t us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-backend:latest .
    docker push us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-backend:latest
```

### Remote build the Docker image and push it to the Artifact Registry
```bash
    gcloud builds submit --tag LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG .
```

Example:
```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-backend:latest .
```


### Deploy Image from Artifact Registry to Cloud Run
```bash
    gcloud run deploy SERVICE_NAME \
        --image=LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG \
        --region=REGION \
        --platform=managed \
        --allow-unauthenticated \
        --port=PORT

```

Example:
```bash
    gcloud run deploy genvid-backend-service \
        --image=us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-backend:latest \
        --region=us-central1 \
        --platform=managed \
        --allow-unauthenticated \
        --port=8080
```

### Run Deploy with ENV 
```bash
    gcloud run deploy SERVICE_NAME \
        --image=LOCATION-docker.pkg.dev/PROJECT_ID/REPOSITORY/IMAGE:TAG \
        --region=REGION \
        --platform=managed \
        --allow-unauthenticated \
        --port=PORT \
        --env-vars-file=PATH_TO_ENV_FILE
```

Example:
```bash
    gcloud run deploy genvid-backend \
        --image=us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-backend:latest \
        --region=us-central1 \
        --platform=managed \
        --allow-unauthenticated \
        --port=8080 \
        --env-vars-file=env.prod.yaml
```


### worker image
```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-worker
```

### deploy the worker as a Cloud Run Job

```bash
gcloud functions deploy video-generation-worker \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source serverless/video_generation \
  --entry-point handle_pubsub \
  --trigger-topic video-generation \
  --set-secrets DATABASE_URL=cloudsql-db-url:latest,REGION=us-central1,PROJECT_ID=genvidgcp,GPU_JOB_NAME=genvid-video-gen-job
``` 
```bash
gcloud functions deploy video-generation-dispatcher \
  --gen2 \
  --runtime python311 \
  --region us-central1 \
  --source serverless/video_generation \
  --entry-point handle_pubsub \
  --trigger-topic video-generation \
  --set-env-vars PROJECT_ID=genvidgcp,REGION=us-central1,GPU_JOB_NAME=genvid-video-gen-job \
  --set-secrets DATABASE_URL=cloudsql-db-url:latest

```

### Cloud Run Job
```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-gpu-worker \
  worker/video_generation 
```

```bash
gcloud run jobs update genvid-video-gen-job \
  --region us-central1 \
  --image us-central1-docker.pkg.dev/genvidgcp/genvid-artifact-repo/genvid-gpu-worker \
  --set-secrets DATABASE_URL=cloudsql-db-url:latest \
  --set-env-vars GCS_BUCKET=genvid-previews,GOOGLE_API_KEY=AIzaSyBcN-K-j3bUafKsORi27Rszxk_GAbUQpSM
```

