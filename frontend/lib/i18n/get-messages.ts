import type { Locale } from "@/lib/i18n/config"
import { DEFAULT_LOCALE, isLocale } from "@/lib/i18n/config"
import { deMessages } from "@/lib/i18n/locales/de.bundle"
import { enMessages } from "@/lib/i18n/locales/en.bundle"
import { frMessages } from "@/lib/i18n/locales/fr.bundle"
import { nlMessages } from "@/lib/i18n/locales/nl.bundle"
import type { AppMessages } from "@/lib/i18n/types"

const table: Record<Locale, AppMessages> = {
  nl: nlMessages,
  de: deMessages,
  fr: frMessages,
  en: enMessages,
}

export function getMessages(raw: string): AppMessages {
  const locale = isLocale(raw) ? raw : DEFAULT_LOCALE
  return table[locale]
}
