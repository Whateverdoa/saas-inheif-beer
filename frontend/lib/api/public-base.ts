/** Production API (FastAPI on Vercel) — same host for all frontend deploys unless overridden. */
export const DEFAULT_PRODUCTION_API_URL = "https://saas-inheif-beer.vercel.app"

function normalizeBase(url: string): string {
  return url.replace(/\/$/, "")
}

function isLocalHostname(hostname: string): boolean {
  return hostname === "localhost" || hostname === "127.0.0.1"
}

/**
 * Base URL for browser calls to the FastAPI backend.
 *
 * Important: `next.config` must not bake `http://localhost:8000` into the client for production.
 * If it does, every deployed user would call their own machine and label-types / KVK would fail.
 */
export function getPublicApiBase(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim()
  let envUrl = raw ? normalizeBase(raw) : ""

  if (typeof window !== "undefined") {
    const host = window.location.hostname
    const pageIsLocal = isLocalHostname(host)
    /** Baked build env often defaults to localhost — ignore that when the app runs on Vercel / real host. */
    if (!pageIsLocal && (envUrl.includes("127.0.0.1") || envUrl.includes("localhost"))) {
      envUrl = ""
    }
    if (envUrl) return envUrl
    if (pageIsLocal) return "http://localhost:8000"
    return DEFAULT_PRODUCTION_API_URL
  }

  /* SSR / tests */
  if (envUrl && !envUrl.includes("localhost") && !envUrl.includes("127.0.0.1")) return envUrl
  return "http://localhost:8000"
}
