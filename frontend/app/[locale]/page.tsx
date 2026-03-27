import { BrewTagShell } from "@/components/brew/BrewTagShell"
import { BrewTagHome } from "@/components/landing/BrewTagHome"
import { DEFAULT_LOCALE, isLocale, type Locale } from "@/lib/i18n/config"
import { getMessages } from "@/lib/i18n/get-messages"

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale: raw } = await params
  const locale: Locale = isLocale(raw) ? raw : DEFAULT_LOCALE
  const messages = getMessages(locale)

  return (
    <BrewTagShell locale={locale} languageNavLabel={messages.nav.language} variant="calm">
      <BrewTagHome home={messages.home} locale={locale} />
    </BrewTagShell>
  )
}
