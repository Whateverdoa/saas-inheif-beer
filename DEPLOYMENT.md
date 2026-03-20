# Deployment Guide (Final)

This project is deployed as **two Vercel projects**:

- **Backend (FastAPI)** from repository root
- **Frontend (Next.js)** from subdirectory `frontend/`

## Live URLs

- Backend API: `https://saas-inheif-beer.vercel.app`
- Frontend app: `https://frontend-inheif.vercel.app`

## Current Architecture

### Backend project (`saas-inheif-beer`)

- Uses `vercel.json` at repo root
- Rewrites all traffic to `api/index.py`
- Python dependencies are installed from `api/requirements.txt`

### Frontend project (`frontend`)

- Root directory in Vercel is `frontend/`
- Uses Next.js build pipeline
- Calls backend with:
  - `NEXT_PUBLIC_API_URL=https://saas-inheif-beer.vercel.app`

## Deploy Commands

### Backend deploy

```bash
# From repository root (where vercel.json and api/ live)
npx vercel --prod --scope inheif
```

### Frontend deploy

```bash
cd frontend
npx vercel --prod --scope inheif
```

## Required Vercel Settings

### Frontend visibility

If frontend shows **Authentication Required**, disable project protection:

1. Open `inheif/frontend`
2. Go to `Settings -> Deployment Protection`
3. Disable **Vercel Authentication**
4. Disable any other protection (password/trusted IP) if enabled

### Frontend env vars

Set in `inheif/frontend -> Settings -> Environment Variables`:

- `NEXT_PUBLIC_API_URL=https://saas-inheif-beer.vercel.app`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<your_value>` (if Clerk is enabled in frontend)

### Backend env vars

Set in `inheif/saas-inheif-beer -> Settings -> Environment Variables`:

- `CLERK_SECRET_KEY=<your_value>` (required for auth endpoints)
- `STRIPE_API_KEY=<your_value>` (if Stripe is enabled)
- `STRIPE_WEBHOOK_SECRET=<your_value>` (if Stripe webhook is used)
- `POLAR_WEBHOOK_SECRET=<your_value>` (if Polar webhook is used)
- `OGOS_API_KEY=<your_value>`
- `OGOS_BASE_URL=https://orders.optimumgroup.nl/OrderService`
- `OGOS_MASTER_GUID=<your_value>` (if B2C flow uses master org)
- `BEER_LABELS_ENABLED=true`

## Smoke Tests

Run after each production deploy:

```bash
curl https://saas-inheif-beer.vercel.app/healthz
curl https://saas-inheif-beer.vercel.app/beer/languages
curl https://saas-inheif-beer.vercel.app/beer/label-types
```

Expected:

- `/healthz` returns `{"ok": true}`
- Beer endpoints return JSON arrays

Then open:

- `https://frontend-inheif.vercel.app`
- `https://frontend-inheif.vercel.app/beer`
- `https://frontend-inheif.vercel.app/beer/compliance`

## Notes and Constraints

- Vercel serverless filesystem is read-only except `/tmp`.
- Current backend uses SQLite fallback in `/tmp` when no external DB is configured.
- `/tmp` storage is ephemeral; data does not persist between cold starts.
- For durable production data, configure external DB and set `DATABASE_URL`.

## Local Development

### Backend

```bash
# From repository root
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Use in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Frontend asks for authentication

- Project-level deployment protection is still enabled on `frontend`.

### Backend returns 500

- Check env vars in backend project.
- Check runtime logs:

```bash
# From repository root
npx vercel logs --scope inheif
```

### CORS issues

- Ensure frontend domain is included in backend CORS allow list in `app/main.py`.

### Frontend shows "Failed to fetch" or "Cannot reach the API"

- **Vercel:** In the **frontend** project, set `NEXT_PUBLIC_API_URL=https://saas-inheif-beer.vercel.app` in **Settings → Environment Variables** (all environments). Redeploy the frontend so the variable is inlined at build time.
- **Local:** In `frontend/.env.local` set `NEXT_PUBLIC_API_URL=http://localhost:8000` and ensure the backend is running.
