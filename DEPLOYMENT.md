# Deployment Guide

## Vercel Deployment

This project consists of two deployable components:
1. **Backend API** (FastAPI) - `/webhooks-skeleton/`
2. **Frontend** (Next.js) - `/webhooks-skeleton/frontend/`

### Prerequisites

- [Vercel CLI](https://vercel.com/docs/cli) installed: `npm i -g vercel`
- Vercel account linked: `vercel login`
- Environment variables ready (see `.env.vercel.example`)

---

## Option 1: Deploy as Monorepo (Recommended)

### Step 1: Initialize Vercel Project

```bash
cd webhooks-skeleton
vercel
```

Follow the prompts:
- Link to existing project? **No** (create new)
- Project name: `ogos-saas`
- Directory: `./` (root)

### Step 2: Configure Build Settings

In Vercel Dashboard > Project Settings > General:

**For Backend (API):**
- Root Directory: `webhooks-skeleton`
- Build Command: (leave empty, uses vercel.json)
- Output Directory: (leave empty)

**For Frontend:**
- Create a separate Vercel project
- Root Directory: `webhooks-skeleton/frontend`
- Framework Preset: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`

### Step 3: Set Environment Variables

In Vercel Dashboard > Project Settings > Environment Variables:

Add all variables from `.env.vercel.example`:

```
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_API_KEY=sk_live_...
POLAR_WEBHOOK_SECRET=...
OGOS_BASE_URL=https://orders.optimumgroup.nl/OrderService
OGOS_API_KEY=...
OGOS_MASTER_GUID=...
CLERK_SECRET_KEY=sk_live_...
CLERK_PUBLISHABLE_KEY=pk_live_...
BEER_LABELS_ENABLED=true
```

### Step 4: Deploy

```bash
# Deploy backend
cd webhooks-skeleton
vercel --prod

# Deploy frontend
cd frontend
vercel --prod
```

---

## Option 2: Deploy Separately

### Backend API Deployment

```bash
cd webhooks-skeleton

# Preview deployment
vercel

# Production deployment
vercel --prod
```

The API will be available at: `https://your-project.vercel.app`

### Frontend Deployment

```bash
cd webhooks-skeleton/frontend

# Set API URL environment variable
# In Vercel Dashboard, add:
# NEXT_PUBLIC_API_URL=https://your-api-project.vercel.app

# Preview deployment
vercel

# Production deployment
vercel --prod
```

---

## Environment Variables Reference

### Backend (Required)

| Variable | Description | Example |
|----------|-------------|---------|
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` |
| `STRIPE_API_KEY` | Stripe API key | `sk_live_...` |
| `OGOS_BASE_URL` | OGOS API base URL | `https://orders.optimumgroup.nl/OrderService` |
| `OGOS_API_KEY` | OGOS API key | `your_key` |
| `CLERK_SECRET_KEY` | Clerk backend secret | `sk_live_...` |

### Backend (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `POLAR_WEBHOOK_SECRET` | Polar webhook secret | - |
| `OGOS_MASTER_GUID` | Master GUID for B2C orders | - |
| `BEER_LABELS_ENABLED` | Enable beer labels feature | `true` |
| `CONVEX_URL` | Convex deployment URL | - |
| `CONVEX_TOKEN` | Convex auth token | - |

### Frontend (Required)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://api.example.com` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk frontend key | `pk_live_...` |

### Frontend (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_CLERK_SIGN_IN_URL` | Sign-in page path | `/sign-in` |
| `NEXT_PUBLIC_CLERK_SIGN_UP_URL` | Sign-up page path | `/sign-up` |
| `NEXT_PUBLIC_BEER_LABELS_ENABLED` | Show beer labels UI | `true` |

---

## Post-Deployment Checklist

### 1. Verify Health Check
```bash
curl https://your-api.vercel.app/healthz
# Expected: {"ok": true}
```

### 2. Test Beer Labels API
```bash
curl https://your-api.vercel.app/beer/label-types
# Expected: JSON array of label types
```

### 3. Configure Webhooks

**Stripe:**
1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://your-api.vercel.app/webhooks/stripe`
3. Select events: `checkout.session.completed`, `invoice.paid`, etc.
4. Copy signing secret to `STRIPE_WEBHOOK_SECRET`

**Polar:**
1. Go to Polar Dashboard > Settings > Webhooks
2. Add endpoint: `https://your-api.vercel.app/webhooks/polar`
3. Copy secret to `POLAR_WEBHOOK_SECRET`

### 4. Configure Clerk

1. Go to Clerk Dashboard > API Keys
2. Copy keys to environment variables
3. Configure allowed origins in Clerk Dashboard

### 5. Test Authentication
```bash
# Get a Clerk session token from your frontend
curl -H "Authorization: Bearer <token>" \
  https://your-api.vercel.app/auth/me
```

---

## Database Considerations

The default SQLite database **will not persist** on Vercel serverless functions.

### Recommended: Use External Database

**Option 1: Vercel Postgres**
```bash
vercel env pull
# Add POSTGRES_URL to your project
```

**Option 2: Supabase**
- Create project at supabase.com
- Copy connection string to `DATABASE_URL`

**Option 3: PlanetScale**
- Create database at planetscale.com
- Copy connection string to `DATABASE_URL`

### Migration Required

Update `app/services/database.py` to use PostgreSQL/MySQL instead of SQLite for production.

---

## Troubleshooting

### Build Fails

1. Check Python version (requires 3.11+)
2. Verify all dependencies in `requirements.txt`
3. Check Vercel build logs

### API Returns 500

1. Check environment variables are set
2. Verify Clerk keys are correct
3. Check Vercel function logs

### CORS Errors

Update `app/main.py` CORS origins:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.vercel.app",
    "https://your-custom-domain.com",
]
```

### Webhook Signature Fails

1. Verify webhook secret is correct
2. Check raw body is being passed (not parsed JSON)
3. Ensure endpoint URL matches exactly

---

## Local Development

### Backend
```bash
cd webhooks-skeleton
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd webhooks-skeleton/frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your keys
npm run dev
```

---

## Support

For issues with:
- **OGOS API**: Contact Optimum Group support
- **Clerk Auth**: https://clerk.com/docs
- **Stripe**: https://stripe.com/docs
- **Vercel**: https://vercel.com/docs
