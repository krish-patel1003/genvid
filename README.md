
# GenVid

AI-powered video generation platform built with a distributed, event-driven architecture on Google Cloud.

GenVid allows users to generate short AI preview videos from text prompts, review them, and optionally publish them to a public feed. The system uses an asynchronous job pipeline powered by Pub/Sub and Cloud Run Jobs to decouple video generation from the main API.

---

## Architecture Overview

```
Frontend
   ↓
FastAPI Backend (Cloud Run)
   ↓
PostgreSQL (Cloud SQL)
   ↓
Pub/Sub
   ↓
Cloud Function (Dispatcher)
   ↓
Cloud Run Job (Worker)
   ↓
Veo API → GCS Upload
   ↓
Database Update
   ↓
SSE → Frontend
```

---

## Detailed Component Diagram

```
┌────────────────────┐
│      Frontend      │
│  (React / Mobile)  │
└─────────┬──────────┘
          │ HTTP / SSE
          ▼
┌──────────────────────────────┐
│ FastAPI Backend (Cloud Run) │
│ - Auth (JWT)                │
│ - Feed                      │
│ - Follow / Like / Comment   │
│ - Signed URL Generation     │
└─────────┬────────────────────┘
          │
          ▼
┌──────────────────────┐
│  PostgreSQL (Cloud   │
│        SQL)          │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│     Google Pub/Sub   │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────────┐
│ Cloud Function Dispatcher│
│ - Marks RUNNING          │
│ - Triggers Cloud Run Job │
└─────────┬────────────────┘
          │
          ▼
┌────────────────────────────┐
│  Cloud Run Job (Worker)   │
│ - Calls Veo API           │
│ - Uploads preview to GCS  │
│ - Updates DB              │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ Google Cloud Storage (GCS)│
│ - Private bucket           │
│ - previews/{job_id}/...    │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│  Signed URL Generation     │
│  (IAM-based, no key files) │
└─────────┬──────────────────┘
          │
          ▼
┌────────────────────────────┐
│ Frontend renders preview   │
│ via temporary signed URL   │
└────────────────────────────┘
```

--- 
## Core Components

### 1. Backend API (FastAPI – Cloud Run)

Responsibilities:

* Authentication (JWT-based)
* User management
* Follow / Unfollow
* Likes & Comments
* Feed generation
* Video generation request endpoint (`POST /generate`)
* SSE endpoint for live job updates
* Signed URL generation for private GCS media

The backend never performs video generation directly.

---

### 2. Dispatcher (Cloud Function)

Triggered via Pub/Sub when a new generation job is created.

Responsibilities:

* Marks job as RUNNING
* Triggers Cloud Run Job
* Handles failure state if dispatch fails

Lightweight and stateless.

---

### 3. Worker (Cloud Run Job)

Independent microservice located in:

```
backend/worker/video_generation/
```

Responsibilities:

* Parses `--job_id` and `--prompt`
* Calls Veo API (4-second preview generation)
* Uploads video to GCS
* Updates database status
* Publishes completion event

No dependency on backend source code.

---

### 4. Storage (Google Cloud Storage)

* Private bucket
* Objects stored under:

```
previews/{job_id}/preview_timestamp.mp4
```

* Signed URLs generated at read-time (not stored in DB)
* IAM-based signing (no private keys)

---

### 5. Database (Cloud SQL – PostgreSQL)

Primary tables:

* users
* videos
* video_generation_jobs
* follows
* likes
* comments

Video generation lifecycle:

```
QUEUED → RUNNING → SUCCEEDED | FAILED
```

---

## Generation Flow

1. User sends prompt via `POST /generate`
2. Backend inserts job with status `QUEUED`
3. Pub/Sub event published
4. Dispatcher triggers Cloud Run Job
5. Worker:

   * Calls Veo API
   * Uploads preview to GCS
   * Updates job status
6. Frontend receives update via SSE
7. User may publish video

---

## Security Model

* No service account JSON files committed
* All secrets stored in:

  * Google Secret Manager
  * Cloud Run environment variables
* Private GCS bucket
* Signed URL generation using IAM
* No public media exposure
* GitHub push protection enforced

---

## Key Design Decisions

* Event-driven job pipeline
* Independent worker microservice
* No shared imports between backend and worker
* Signed URLs generated at response time
* Private bucket, no public access
* 4-second preview generation to reduce cost
* ffmpeg avoided for memory safety
* IAM-based signing (no key files)

---

## Future Improvements

* Replace API key auth with Vertex AI auth
* Retry & backoff logic for job failures
* Job cancellation support
* Cloud CDN for media delivery
* Multi-instance SSE push system
* Generation cost guardrails
* Metrics & monitoring

---

## Technologies Used

* Python
* FastAPI
* SQLModel
* PostgreSQL
* Google Cloud Run
* Google Cloud Functions
* Google Pub/Sub
* Google Cloud Storage
* Veo (Google GenAI)
* SSE (Server-Sent Events)

---

## Author

Krish Patel
Date: Feb 2026
