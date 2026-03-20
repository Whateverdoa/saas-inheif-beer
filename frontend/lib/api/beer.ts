import { getPublicApiBase } from "./public-base"

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const base = getPublicApiBase()
  const url = path.startsWith("http") ? path : `${base}${path}`
  const res = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export interface BeerCategory {
  value: string
  label: string
  description?: string
}

export interface BeerLabelType {
  id: string
  name: string
  category: string
  width_mm: number
  height_mm: number
  description?: string
  recommended_substrates: string[]
}

export interface BeerSubstrate {
  code: string
  name: string
  material_id: number
  is_waterproof: boolean
  is_biodegradable: boolean
  finish: string
  description?: string
}

export interface EULanguage {
  code: string
  native_name: string
  english_name: string
}

export interface ComplianceTextResponse {
  [langCode: string]: {
    ingredients_label: string
    ingredients_text: string
    contains_label: string
    allergens_text: string
    abv_label: string
    abv_text: string
    producer_label: string
    producer_text: string
    country_label: string
    country_text: string
    warning_text: string
    age_warning: string
  }
}

export const beerApi = {
  async getCategories(): Promise<BeerCategory[]> {
    return fetchJson<BeerCategory[]>("/beer/categories")
  },

  async getLabelTypes(): Promise<BeerLabelType[]> {
    return fetchJson<BeerLabelType[]>("/beer/label-types")
  },

  async getSubstrates(): Promise<BeerSubstrate[]> {
    return fetchJson<BeerSubstrate[]>("/beer/substrates")
  },

  async getLanguages(): Promise<EULanguage[]> {
    return fetchJson<EULanguage[]>("/beer/languages")
  },

  async generateComplianceText(body: {
    languages: string[]
    abv: number
    ingredients: string[]
    allergens: string[]
    producer: string
    country: string
  }): Promise<ComplianceTextResponse> {
    return fetchJson<ComplianceTextResponse>("/beer/compliance-text", {
      method: "POST",
      body: JSON.stringify(body),
    })
  },
}
