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

## Optioneel: GitHub Action

Alleen als je deploy **via Actions** wilt: repo-variable **`VERCEL_ACTIONS_DEPLOY=true`** + secrets.  
De workflow deployt vanuit **`frontend/`** met `vercel deploy .` (niet `vercel deploy frontend`), anders zoekt Vercel naar `frontend/frontend` en faalt de build.

Wil je het **simpel** houden: zet **`VERCEL_ACTIONS_DEPLOY` uit** (variable verwijderen of niet `true`) en gebruik alleen Vercel Git hierboven.

## Snel troubleshooten

| Symptoom | Meest waarschijnlijk |
|----------|----------------------|
| Site (`frontend-inheif`) niet nieuw na merge | Project **`frontend`** niet gekoppeld, verkeerde Root Directory, of build **fout** (oude groene deploy blijft staan). |
| Alleen API lijkt nieuw | Je kijkt naar **`saas-inheif-beer`**; dat is **niet** de Next-site. |
| Action: path `frontend/frontend` | Oude workflow; pull `main` — deploy moet **`cd frontend` + `vercel deploy .`** zijn. |

Meer detail: **[../DEPLOYMENT.md](../DEPLOYMENT.md)**.
