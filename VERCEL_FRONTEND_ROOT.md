# Build failed: “No Next.js version detected”

That error **always** means Vercel is building from the **wrong folder**.

This repo has **two** Vercel projects:

| Project             | Root Directory must be |
|---------------------|-------------------------|
| `saas-inheif-beer`  | **`.`** (repo root) — FastAPI |
| `frontend`          | **`frontend`** — Next.js |

## Fix (2 minutes)

1. Open [Vercel Dashboard](https://vercel.com) → team **Inheif** → project **`frontend`** (not `saas-inheif-beer`).
2. **Settings** → **General** → **Root Directory**
3. Click **Edit** → type **`frontend`** (no slash, no dot) → **Save**
4. **Deployments** → open the failed deployment → **⋯** → **Redeploy**

After this, the build uses `frontend/package.json` where `"next"` is listed and the error disappears.

## Why it happens

The **repository root** `package.json` only has tooling (`vercel`, Playwright). It has **no** `next` dependency. If Root Directory is empty or `.`, Vercel runs there and correctly says Next.js is missing.

## More detail

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** (two-project setup, env vars, URLs).
