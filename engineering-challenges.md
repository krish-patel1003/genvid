# Engineering Challenges & How They Were Solved

This document outlines the major technical challenges encountered while building GenVid and the engineering decisions taken to resolve them.

---

## 1️⃣ Designing a Non-Blocking Video Generation Pipeline

### The Problem

Video generation is computationally expensive and slow. Running it directly inside the FastAPI backend would:

* Block request threads
* Increase latency dramatically
* Cause timeouts
* Make the API horizontally unscalable

### The Solution

Designed an event-driven architecture:

```
API → Pub/Sub → Dispatcher → Cloud Run Job → Worker
```

Key design decisions:

* Backend only creates a job record (`QUEUED`)
* Pub/Sub decouples API from generation
* Cloud Function acts as lightweight dispatcher
* Cloud Run Job handles heavy compute

This made the API:

* Stateless
* Fast
* Horizontally scalable

---

## 2️⃣ Preventing Secret Leaks (GitHub Push Protection Incident)

### The Problem

Accidentally committed:

* Google Cloud service account JSON
* OAuth client secret
* Production environment file

GitHub push protection blocked the push.

### The Risks

* Compromised credentials
* Production environment takeover
* Billing abuse
* Data exfiltration

### The Solution

1. Immediately rotated all exposed secrets
2. Deleted compromised service account keys
3. Regenerated OAuth client secrets
4. Rewrote Git history using `git filter-repo`
5. Force-pushed cleaned history
6. Moved all secrets to:

   * Secret Manager
   * Cloud Run environment variables
7. Updated `.gitignore`

### Outcome

Established a proper secret management workflow and avoided future leaks.

---

## 3️⃣ Signed URL Generation in Cloud Run (No Private Key)

### The Problem

When generating signed URLs for private GCS objects, the backend threw:

```
you need a private key to sign credentials
```

Cloud Run provides token-based credentials, not private keys.

### Why It Happened

* `generate_signed_url()` defaults to private-key signing
* Cloud Run service accounts do not expose private keys
* Library version did not auto-switch to IAM signing

### The Solution

* Enabled IAM Credentials API
* Granted `roles/iam.serviceAccountTokenCreator`
* Used `compute_engine.IDTokenCredentials`
* Passed explicit service account email for signing

This allowed secure IAM-based signing without storing private key files.

### Outcome

* Private bucket retained
* No public media exposure
* Production-grade signing implemented

---

## 4️⃣ Memory Explosion When Expanding Videos

### The Problem

Attempted to expand a 4-second video to 30 seconds using:

```python
imageio.mimread()
```

This loaded entire video frames into memory and triggered:

```
RuntimeError: imageio.mimread() has read over 256000000B
```

### The Solution

Replaced frame-based expansion with ffmpeg stream-level looping:

```bash
ffmpeg -stream_loop 7 -i input.mp4 -c copy -t 30 output.mp4
```

Benefits:

* No full memory load
* No re-encoding
* Faster
* Production-safe

Eventually removed expansion entirely and kept 4-second preview.

---

## 5️⃣ VEO Returning Black Frames

### The Problem

Generated videos appeared as black frames.

### Root Cause

Prompt included copyrighted / trademarked entities:

* "Disneyland"
* "Superhero"

Veo returned safe-filtered blank output.

### The Solution

* Modified prompts to avoid trademarked content
* Tested generation locally
* Verified raw 4-second clip before expansion

### Outcome

Established a content safety-aware prompt strategy.

---

## 6️⃣ Cloud Run Job Argument Parsing Issues

### The Problem

Passing JSON to Cloud Run Job via:

```
--args='{"job_id":1,"prompt":"test"}'
```

Resulted in:

```
JSONDecodeError
```

### Root Cause

CLI splits `--args` by commas.

### The Solution

Switched to structured arguments:

```python
parser.add_argument("--job_id")
parser.add_argument("--prompt")
```

Dispatcher now sends:

```
--job_id 1 --prompt "Test"
```

Cleaner and production-safe.

---

## 7️⃣ SSE Not Updating in Real Time

### The Problem

SSE connection opened but frontend did not update until refresh.

### Root Cause

* Reused DB session inside infinite loop
* Stale transaction snapshot
* Frontend reconnect loop due to dependency array

### The Solution

* Created fresh DB session inside SSE loop
* Added heartbeat ping
* Removed unnecessary frontend re-subscriptions

### Outcome

Live updates work without page refresh.

---

## 8️⃣ GPU Quota & Zonal Redundancy Issues

### The Problem

Cloud Run GPU Job creation failed with:

```
You do not have quota for using GPUs without zonal redundancy
```

### The Solution

* Temporarily switched to CPU mode
* Requested GPU quota
* Kept architecture GPU-ready

### Lesson

Always design infra to degrade gracefully when quota is unavailable.

---

## 9️⃣ Balancing Simplicity vs Over-Engineering

There was a design decision between:

* Poll-based worker
* Pub/Sub push model
* Long-running GPU service
* Hybrid dispatcher pattern

Chose:

```
Pub/Sub → Dispatcher → Cloud Run Job
```

Because:

* Clean separation of concerns
* Scalable
* Easier to reason about
* Independent services

---

# Key Engineering Lessons

1. Secrets must never enter Git history.
2. Cloud Run credentials are token-based — not key-based.
3. Event-driven systems reduce coupling dramatically.
4. Test heavy compute locally before deploying infra.
5. Design for scale, but don’t over-engineer prematurely.
6. Always validate raw outputs before blaming infra.

---

# Final Takeaway

GenVid evolved from a simple API idea into a distributed system requiring:

* Asynchronous job orchestration
* Secure credential handling
* Cloud-native signing mechanisms
* Event-driven architecture
* Cross-service coordination

The major challenges were not model-related — they were architectural and infrastructure-driven.


