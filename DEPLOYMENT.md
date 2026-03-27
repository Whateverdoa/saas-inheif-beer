# Deployment Guide (Final)

**Dashboard links & live URLs:** **[docs/DASHBOARDS.md](./docs/DASHBOARDS.md)**.

**Nieuw hier?** Lees eerst **[docs/VERCEL_BEGRIJPEN.md](./docs/VERCEL_BEGRIJPEN.md)** (API vs site, zonder Action).

This GitHub repo connects to **two separate Vercel projects** (same team, e.g. `inheif`):

| Vercel project name | What it is | Root Directory in Vercel | Production URL (typical) |
|---------------------|------------|---------------------------|---------------------------|
| **`saas-inheif-beer`** | Backend — FastAPI on Python serverless | **Repository root** (`.`) | `https://saas-inheif-beer.vercel.app` |
| **`frontend`** | Frontend — Next.js app | **`frontend/`** subdirectory | `https://frontend-inheif.vercel.app` |

### Critical: frontend Root Directory

If the **`frontend`** Vercel project has Root Directory left as **repository root** (`.`), the build fails with:

**`Build Failed` — `No Next.js version detected`. Make sure your package.json has "next" … **Also check your Root Directory setting** …**

That message is **misleading**: the repo-root `package.json` intentionally has **no** `next` (only the Python API + tooling). The Next.js app is in **`frontend/package.json`**.

**Fix (one-time):** Vercel → project **`frontend`** (not `saas-inheif-beer`) → **Settings → General** → **Root Directory** → **`frontend`** → Save. Then **Deployments → Redeploy**.

Short reference: **[VERCEL_FRONTEND_ROOT.md](./VERCEL_FRONTEND_ROOT.md)**.

Until this is set, **Production keeps serving the last successful deploy** (older UI). Merging PRs will not update the live site.

**Also:** UI changes appear on **`frontend-inheif.vercel.app`**, not on `saas-inheif-beer.vercel.app` (that URL is the API).

Each project has its **own** Vercel dashboard, env vars, and deployments. Pushes to `main` can trigger **both** if both are linked to the same repo with the correct root directories.

## PR → preview; merge → productie (site)

**Doel:** elke **PR** krijgt een **Preview-URL** met de nieuwe UI; na **merge naar `main`** gaat **productie** (`frontend-inheif.vercel.app`) mee.

### Aanbevolen: Vercel Git-integratie (geen extra CI)

1. **GitHub:** [Vercel GitHub App](https://github.com/apps/vercel) installeren op de **organisatie/user** die deze repo bevat (toegang tot deze repo).
2. **Vercel → project `frontend`:** **Settings → Git** → dezelfde repo koppelen, **Production branch** = `main`.
3. **Root Directory** = `frontend` (zie hierboven).
4. Bij elke **push naar een PR-branch** maakt Vercel een **Preview deployment**; de bot post (meestal) een link op de PR. Na **merge** → **Production** voor dat project.

**Let op:** het project **`saas-inheif-beer`** is de **API**; de **site** is **`frontend`**. Alleen als **`frontend`** mee-deployt zie je UI-wijzigingen op `frontend-inheif.vercel.app`.

### Optioneel: GitHub Action (zelfde gedrag, expliciet)

Als previews/productie niet automatisch lopen, kun je **[`.github/workflows/vercel-frontend.yml`](./.github/workflows/vercel-frontend.yml)** gebruiken:

| GitHub → Actions | Waarde |
|------------------|--------|
| **Secret** | `VERCEL_TOKEN` — [Vercel account tokens](https://vercel.com/account/tokens) |
| **Secret** | `VERCEL_ORG_ID` — team-id (`team_…`, Vercel team settings) |
| **Secret** | `VERCEL_PROJECT_ID_FRONTEND` — project-id (`prj_…`) van het Vercel-project **`frontend`** |

- **PR** (zelfde repo; wijzigingen onder `frontend/`) → **preview** deploy (`vercel deploy frontend`, officiële CLI).  
- **Push naar `main`** → **`--prod`** (productie).

De workflow zet `VERCEL_ORG_ID` en `VERCEL_PROJECT_ID` (GitHub-secret **`VERCEL_PROJECT_ID_FRONTEND`**) zoals de Vercel CLI verwacht.

**Dubbele builds:** Vercel Git **en** deze Action tegelijk → twee builds. Kies één route of disconnect Git deploy voor `frontend`.

## Automatic deploys (push / PR)

With **Git connected** on each Vercel project, you do **not** need a custom GitHub Action for normal flows:

| Git event | What happens |
|-----------|----------------|
| **Push to a branch** (e.g. PR branch) | **Preview deployment** — unique URL per branch/commit (PR comments if the Vercel GitHub app is installed on the org/repo). |
| **Merge to the Production branch** (usually `main`) | **Production deployment** for that project. |

The **`frontend`** and **`saas-inheif-beer`** projects each run their own build from the **same commit**; configure **Root Directory** separately (`frontend/` vs `.`).

**If Production looks stale:** compare the deployment’s **git SHA** to GitHub `main`. Failed builds leave the last green Production deploy in place — fix the build, then merge or push again. Prefer redeploying from the **latest** commit, not an old successful one.

**Checklist (both projects):** **Settings → Git** → correct repo, **Production Branch** = `main`; **Ignored Build Step** only if you really mean to skip.

### Frontend deployt automatisch na merge — zo zet je het goed

Vercel start zelf een **production build** bij een merge naar `main`; er is geen aparte “frontend oppicken”-stap als het project juist staat:

| Stap | Vercel → project **`frontend`** | Waarde |
|------|-----------------------------------|--------|
| 1 | **Settings → Git → Connected Git Repository** | Dezelfde GitHub-repo als de backend |
| 2 | **Production Branch** | `main` |
| 3 | **Settings → General → Root Directory** | `frontend` |
| 4 | **Settings → Git → Ignored Build Step** | **Leeg** (aanbevolen) → elke merge naar `main` bouwt de frontend opnieuw |

**GitHub:** de **Vercel**-integratie moet op de repo staan (anders geen deploy bij push/merge).

**Optioneel — minder builds:** alleen bouwen als `frontend/` wijzigt. **Ignored Build Step:**

```bash
git diff HEAD^ HEAD --quiet ./frontend/
```

(exit **0** = geen wijzigingen onder `frontend/` → skip build; exit **1** → wél builden.)

## Live URLs

- **Backend (project `saas-inheif-beer`):** `https://saas-inheif-beer.vercel.app`
- **Frontend (project `frontend`):** `https://frontend-inheif.vercel.app`

## Frontend locales (NL / DE / FR / EN)

All app routes live under a **locale prefix**: `/{nl|de|fr|en}/…`. Visiting `/` redirects to the best match from the `NEXT_LOCALE` cookie (if set), then `Accept-Language`, otherwise **`nl`**.

Examples:

- `https://frontend-inheif.vercel.app/nl/beer/order`
- `https://frontend-inheif.vercel.app/en/beer`

The **language switcher** (top-right on BrewTag pages) updates the URL and sets the `NEXT_LOCALE` cookie for later visits.

## Current Architecture

### 1. Backend Vercel project: `saas-inheif-beer`

- Git: **entire repo**, but Vercel **Root Directory** = `.` (repo root)
- Uses `vercel.json` at repo root
- Rewrites all traffic to `api/index.py`
- Python dependencies from `api/requirements.txt`

### 2. Frontend Vercel project: `frontend`

- Git: **same repo**, Vercel **Root Directory** = `frontend/`
- Next.js build (`npm run build`)
- Calls the API using **`NEXT_PUBLIC_API_URL`** = your backend URL, e.g. `https://saas-inheif-beer.vercel.app`

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

1. Open Vercel project **`frontend`** (team `inheif`)
2. Go to `Settings -> Deployment Protection`
3. Disable **Vercel Authentication**
4. Disable any other protection (password/trusted IP) if enabled

### Frontend env vars (project **`frontend`**)

Vercel → project **`frontend`** → **Settings → Environment Variables**:

- `NEXT_PUBLIC_API_URL=https://saas-inheif-beer.vercel.app`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<your_value>` (if Clerk is enabled in frontend)

### Backend env vars (project **`saas-inheif-beer`**)

Vercel → project **`saas-inheif-beer`** → **Settings → Environment Variables**:

- `CLERK_SECRET_KEY=<your_value>` (required for auth endpoints)
- `STRIPE_API_KEY=<your_value>` (if Stripe is enabled)
- `STRIPE_WEBHOOK_SECRET=<your_value>` (if Stripe webhook is used)
- `POLAR_WEBHOOK_SECRET=<your_value>` (if Polar webhook is used)
- `OGOS_API_KEY=<your_value>`
- `OGOS_BASE_URL=https://orders.optimumgroup.nl/OrderService`
- `OGOS_MASTER_GUID=<your_value>` (if B2C flow uses master org)
- `BEER_LABELS_ENABLED=true`
- `KVK_API_KEY=<your_value>` (optional — [KVK Basisprofiel API](https://developers.kvk.nl); without it, only test KVK `12345678` / `69599084` work via built-in mock)

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

Then open (frontend project):

- `https://frontend-inheif.vercel.app`
- `https://frontend-inheif.vercel.app/beer`
- `https://frontend-inheif.vercel.app/beer/order` (quote form + KVK lookup)
- `https://frontend-inheif.vercel.app/beer/compliance`

Optional API check (backend project):

```bash
curl "https://saas-inheif-beer.vercel.app/kvk/lookup/12345678"
```

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
