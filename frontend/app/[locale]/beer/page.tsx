import { BeerLabelsConfigurator } from "@/components/beer/BeerLabelsConfigurator"
import { DEFAULT_LOCALE, isLocale, type Locale } from "@/lib/i18n/config"
import { getMessages } from "@/lib/i18n/get-messages"

export default async function BeerPage({
  params,
}: {
  params: Promise<{ locale: string }>
}) {
  const { locale: raw } = await params
  const locale: Locale = isLocale(raw) ? raw : DEFAULT_LOCALE
  const messages = getMessages(locale)

  return <BeerLabelsConfigurator key={locale} t={messages.beerTool} locale={locale} />
}
