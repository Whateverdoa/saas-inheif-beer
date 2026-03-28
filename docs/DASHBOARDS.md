# Live dashboards & production URLs

**Team:** Inheif (`team_bxxTuh7s852O8AUxNADEH3Y9`)  
**Last verified:** 2026-03-27 (HTTP smoke tests below)

## Vercel (browser)

| Open this | What it is |
|-----------|------------|
| [Vercel — Inheif team](https://vercel.com/inheif) | All projects, billing, domains |
| [Project **frontend** (Next.js)](https://vercel.com/inheif/frontend) | BrewTag UI — set **Root Directory** = `frontend` |
| [Project **saas-inheif-beer** (FastAPI)](https://vercel.com/inheif/saas-inheif-beer) | Python serverless API at repo root |

**Production domains (Vercel):**

- Frontend: `https://frontend-inheif.vercel.app` (locales: `/nl`, `/en`, `/de`, `/fr`, …)
- API (serverless): `https://saas-inheif-beer.vercel.app`

**Latest production deployments** were **READY** (commit `8ec3471…` on `main` for both Git-linked projects).

### Related: `inheif-saas-ogos-api` repo

If you use the older monorepo frontend project:

- [Project **inheif-saas-ogos-web-new**](https://vercel.com/inheif/inheif-saas-ogos-web-new)

## Digital Ocean — App Platform

| Open this | What it is |
|-----------|------------|
| [App **inheif-saas-ogos-api**](https://cloud.digitalocean.com/apps/82061f9a-e2d8-4a9c-a547-26928586d75c) | Runtime, env vars, deploy history, logs |

**Public URL:** `https://inheif-saas-ogos-api-u22ws.ondigitalocean.app`  
**Source:** GitHub `Whateverdoa/saas-inheif-beer` branch **`main`** (component `api`).

## PDF preflight (API)

Public endpoint (no auth): **`POST /beer/preflight-pdf`** with multipart field **`file`** (`.pdf`).

- Swagger: `https://<api-host>/docs` → **beer** → `preflight_pdf`
- Example:

```bash
curl -sS -X POST "https://inheif-saas-ogos-api-u22ws.ondigitalocean.app/beer/preflight-pdf" \
  -F "file=@/path/to/label.pdf" | jq .
```

Returns `PDFValidationResult` JSON (`is_valid`, `errors`, `warnings`, `page_count`, boxes, `color_space`, etc.).

## Quick smoke checks (terminal)

```bash
# DO backend
curl -fsS https://inheif-saas-ogos-api-u22ws.ondigitalocean.app/healthz
# expect: {"ok":true}

# Vercel FastAPI
curl -fsS https://saas-inheif-beer.vercel.app/healthz

# Frontend (SSR)
curl -fsS -o /dev/null -w "%{http_code}\n" https://frontend-inheif.vercel.app/nl
# expect: 200
```

## GitHub Actions

Frontend deploy workflow: [`.github/workflows/vercel-frontend.yml`](../.github/workflows/vercel-frontend.yml)  
Secrets: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID_FRONTEND`.

If both **Vercel Git** and this workflow deploy the same project, you may see duplicate builds — pick one path (see `DEPLOYMENT.md`).
