/** Supported UI locales (path prefix). */

export const LOCALES = ["nl", "de", "fr", "en"] as const

export type Locale = (typeof LOCALES)[number]

export const DEFAULT_LOCALE: Locale = "nl"

export const LOCALE_LABELS: Record<Locale, string> = {
  nl: "NL",
  de: "DE",
  fr: "FR",
  en: "EN",
}

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value)
}

/** Prefix a path that does not already include a locale segment. */
export function withLocale(locale: Locale, path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`
  if (LOCALES.some((l) => p === `/${l}` || p.startsWith(`/${l}/`))) {
    return p
  }
  return p === "/" ? `/${locale}` : `/${locale}${p}`
}
