# Spam Shield: Deployment & Operations Guide

This guide covers step-by-step production deployment for the Spam Shield FastAPI backend, Supabase database, and Flutter mobile client.

---

## 1. Secrets & Environment Configuration

Copy the example configuration to your environment file:
```bash
cp backend/.env.example backend/.env
```

Ensure the following variables are populated in `backend/.env`:
```env
# Groq API Configuration (Layer 3 LLM Second Opinion)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
GROQ_FALLBACK_MODEL=openai/gpt-oss-20b
RATE_LIMIT_GROQ_PER_USER_PER_DAY=50

# Supabase Database Configuration (Telemetry & Caching)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_supabase_anon_key
SUPABASE_SECRET_KEY=your_supabase_service_role_key
```

> **Security Rule:** Never commit `backend/.env` to version control. The root `.gitignore` protects this automatically.

---

## 2. Supabase Database Setup

1. Open your project on [Supabase Dashboard](https://supabase.com/dashboard).
2. Navigate to **SQL Editor** -> **New Query**.
3. Copy and execute the contents of `backend/schema.sql`:
   - Creates `public.llm_cache` table with SHA-256 index.
   - Creates `public.scan_logs` table for telemetry.
   - Creates `public.user_feedback` table for retraining.
   - Configures Row Level Security (RLS) policies.
4. If you run without Supabase credentials or before executing the migration, the backend automatically activates its resilient in-memory storage fallback.

---

## 3. Backend Deployment

### Option A: Render.com (Recommended Free/Starter)
1. Fork or push the repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com), click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following build settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. In **Environment Variables**, add `GROQ_API_KEY`, `SUPABASE_URL`, and `SUPABASE_SECRET_KEY`.
6. Click **Deploy Web Service**.

### Option B: Docker Container
Build and run the containerized backend:
```bash
# Build Docker image
docker build -t spam-shield-api -f backend/Dockerfile .

# Run container
docker run -d -p 8000:8000 --env-file backend/.env --name spam-shield spam-shield-api
```

---

## 4. Mobile Client Build & Release

### Automated GitHub Actions CI/CD
Every commit or tag push triggers `.github/workflows/apk_release.yml`, which runs unit/widget tests and compiles `app-release.apk` as a downloadable GitHub Actions artifact.

### Local Compilation
To compile the release APK locally:
```bash
cd mobile
flutter pub get
flutter test
flutter build apk --release
```
The output binary will be located at:
`mobile/build/app/outputs/flutter-apk/app-release.apk`

---

## 5. Production Health Verification

Verify backend operational status with cURL:
```bash
# Health check
curl -X GET https://your-backend-url/health

# Performance metrics
curl -X GET https://your-backend-url/metrics

# Test scan
curl -X POST https://your-backend-url/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Your SBI account is blocked due to KYC. Update at http://192.168.1.1/sbi.apk"}'
```
