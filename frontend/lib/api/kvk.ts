import { getPublicApiBase } from "./public-base"

export interface KvkCompany {
  kvk_number: string
  name: string
  statutaire_naam?: string | null
  rechtsvorm?: string | null
  street?: string | null
  house_number?: string | null
  house_number_addition?: string | null
  postal_code?: string | null
  city?: string | null
  full_address: string
  source?: string
}

export async function lookupKvk(kvkNummer: string): Promise<KvkCompany> {
  const base = getPublicApiBase()
  const normalized = kvkNummer.replace(/\s+/g, "")
  const res = await fetch(`${base}/kvk/lookup/${encodeURIComponent(normalized)}`)
  if (!res.ok) {
    let msg = `HTTP ${res.status}`
    try {
      const body = await res.json()
      if (body?.detail) msg = typeof body.detail === "string" ? body.detail : msg
    } catch {
      /* ignore */
    }
    throw new Error(msg)
  }
  return res.json() as Promise<KvkCompany>
}
