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

export type PDFBox = {
  x0: number
  y0: number
  x1: number
  y1: number
}

/** Mirrors FastAPI `PDFValidationResult` (preflight + geometry hints). */
export interface PDFValidationResult {
  is_valid: boolean
  errors: string[]
  warnings: string[]
  file_size: number
  page_count: number
  trimbox: PDFBox | null
  bleedbox: PDFBox | null
  mediabox: PDFBox | null
  color_space: string | null
  is_cmyk: boolean
  metadata: Record<string, unknown>
  trim_width_mm?: number | null
  trim_height_mm?: number | null
  media_width_mm?: number | null
  media_height_mm?: number | null
  bleed_insets_mm?: Record<string, number> | null
  dimensions_display?: string | null
  suggested_shape?: string | null
  matched_standard_label_type_id?: string | null
  matched_standard_label_name?: string | null
  match_distance_mm?: number | null
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

  async preflightLabelPdf(
    file: File,
    init?: { signal?: AbortSignal }
  ): Promise<PDFValidationResult> {
    const base = getPublicApiBase()
    const fd = new FormData()
    fd.append("file", file)
    const res = await fetch(`${base}/beer/preflight-pdf`, {
      method: "POST",
      body: fd,
      signal: init?.signal,
    })
    if (!res.ok) {
      const text = await res.text()
      throw new Error(text || `HTTP ${res.status}`)
    }
    return res.json() as Promise<PDFValidationResult>
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
