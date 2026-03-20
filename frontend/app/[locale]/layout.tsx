import type { Metadata } from "next"

import { DEFAULT_LOCALE, isLocale, LOCALES } from "@/lib/i18n/config"
import { getMessages } from "@/lib/i18n/get-messages"

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>
}): Promise<Metadata> {
  const { locale: raw } = await params
  const locale = isLocale(raw) ? raw : DEFAULT_LOCALE
  const m = getMessages(locale)
  return {
    title: m.meta.title,
    description: m.meta.description,
    keywords: ["beer labels", "etiketten", "bier", "Vila-bier", "Vila-etiketten", "Vrijmibo"],
  }
}

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }))
}

export default function LocaleLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
