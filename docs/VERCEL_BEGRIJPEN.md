# Vercel + deze repo — kort uitgelegd

## Wat je hebt (1 Git-repo, 2 Vercel-projecten)

| Wat | Vercel-projectnaam | URL (voorbeeld) | Root Directory in Vercel |
|-----|---------------------|-------------------|---------------------------|
| **API** (Python) | `saas-inheif-beer` | `saas-inheif-beer.vercel.app` | **`.`** (repo-root) |
| **Website** (Next.js) | `frontend` | `frontend-inheif.vercel.app` | **`frontend`** |

**PR’s en pushes gaan altijd naar GitHub.** Vercel bouwt **apart** per project: alleen het project dat goed aan Git hangt én de juiste Root Directory heeft, krijgt een nieuwe deploy.

- Wijzig je **alleen** API → vooral `saas-inheif-beer`-deploy.
- Wijzig je **de site** → het project **`frontend`** moet deployen (niet alleen `saas-inheif-beer`).

## Aanbevolen (minst ingewikkeld): géén GitHub Action

1. [Vercel](https://vercel.com) → project **`frontend`**.
2. **Settings → Git**: zelfde GitHub-repo, branch **`main`**.
3. **Settings → General → Root Directory**: **`frontend`** (exact zo).
4. GitHub: [Vercel App](https://github.com/apps/vercel) installeren op je account/org met toegang tot de repo.

Dan: **push / PR** → Vercel maakt zelf **Previews**; **merge naar `main`** → **productie**.

Geen secrets in GitHub nodig.

## GitHub Action (in deze repo)

Workflow **Deploy frontend**: draait op **elke PR** (zelfde repo) en **elke push naar `main`**. Vereist de drie **repository secrets** (`VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID_FRONTEND`). Deploy: `frontend/` + `vercel deploy .`.

## Snel troubleshooten

| Symptoom | Meest waarschijnlijk |
|----------|----------------------|
| Site (`frontend-inheif`) niet nieuw na merge | Project **`frontend`** niet gekoppeld, verkeerde Root Directory, of build **fout** (oude groene deploy blijft staan). |
| Alleen API lijkt nieuw | Je kijkt naar **`saas-inheif-beer`**; dat is **niet** de Next-site. |
| Action: path `frontend/frontend` | Oude workflow; pull `main` — deploy moet **`cd frontend` + `vercel deploy .`** zijn. |

Meer detail: **[../DEPLOYMENT.md](../DEPLOYMENT.md)**.
