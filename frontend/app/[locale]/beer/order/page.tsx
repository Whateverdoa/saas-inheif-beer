import { BrewTagShell } from "@/components/brew/BrewTagShell"
import { BeerOrderForm } from "@/components/order/BeerOrderForm"
import { DEFAULT_LOCALE, isLocale, type Locale } from "@/lib/i18n/config"
import { getMessages } from "@/lib/i18n/get-messages"

export default async function BeerOrderPage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale: raw } = await params
  const locale: Locale = isLocale(raw) ? raw : DEFAULT_LOCALE
  const messages = getMessages(locale)

  return (
    <BrewTagShell locale={locale} languageNavLabel={messages.nav.language}>
      <BeerOrderForm kvk={messages.kvk} messages={messages.order} locale={locale} />
    </BrewTagShell>
  )
}
