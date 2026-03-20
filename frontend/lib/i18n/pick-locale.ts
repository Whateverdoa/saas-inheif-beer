import type { Locale } from "@/lib/i18n/config"
import { DEFAULT_LOCALE } from "@/lib/i18n/config"

/**
 * Map Accept-Language to a supported locale (first match wins).
 */
export function pickLocaleFromAcceptLanguage(header: string | null): Locale {
  if (!header || !header.trim()) return DEFAULT_LOCALE

  const parts = header.split(",")
  for (const part of parts) {
    const tag = part.trim().split(";")[0]?.toLowerCase()
    if (!tag) continue
    const primary = tag.split("-")[0]
    if (primary === "nl") return "nl"
    if (primary === "de") return "de"
    if (primary === "fr") return "fr"
    if (primary === "en") return "en"
  }
  return DEFAULT_LOCALE
}
