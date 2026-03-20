/** Production API URL when env is missing in Vercel builds. */
const PRODUCTION_API_URL = "https://saas-inheif-beer.vercel.app"

/**
 * Base URL for browser calls to the FastAPI backend (direct or via Next rewrite).
 */
export function getPublicApiBase(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_URL
  if (envUrl) return envUrl.replace(/\/$/, "")
  if (typeof window !== "undefined") {
    if (window.location.origin.includes("frontend-inheif.vercel.app"))
      return PRODUCTION_API_URL
    return "/api/backend"
  }
  return "http://localhost:8000"
}
