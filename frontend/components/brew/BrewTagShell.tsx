import type { ReactNode } from "react"

import { BeerBubbles } from "@/components/brew/BeerBubbles"
import { BeerFoamCollar, BEER_FOAM_COLLAR_HEIGHT_PX } from "@/components/brew/BeerFoamCollar"
import { LocaleSwitcher } from "@/components/i18n/LocaleSwitcher"
import type { Locale } from "@/lib/i18n/config"

/**
 * BrewTag-inspired shell: golden beer gradient, glass highlights, condensation specks.
 */
export function BrewTagShell({
  children,
  locale,
  languageNavLabel,
}: {
  children: ReactNode
  locale: Locale
  languageNavLabel: string
}) {
  return (
    <div className="font-brew-sans min-h-screen text-[#4a2800] relative overflow-x-hidden">
      <div className="fixed top-4 right-4 z-[100] flex justify-end">
        <LocaleSwitcher current={locale} navLabel={languageNavLabel} />
      </div>
      <div
        className="fixed inset-0 -z-10"
        style={{
          background:
            "linear-gradient(180deg, #f2cc44 0%, #e6b41a 15%, #d4a012 35%, #c08a0c 55%, #a67206 75%, #8b6508 100%)",
        }}
      />
      <div
        aria-hidden
        className="fixed inset-0 -z-10 pointer-events-none opacity-50"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 50% 35%, rgba(242,204,68,0.25) 0%, rgba(230,180,26,0.12) 40%, transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="fixed top-0 left-0 w-16 h-full -z-10 pointer-events-none"
        style={{
          background: "linear-gradient(90deg, rgba(255,245,200,0.35) 0%, transparent 100%)",
        }}
      />
      <div
        aria-hidden
        className="fixed top-0 right-0 w-20 h-full -z-10 pointer-events-none"
        style={{
          background: "linear-gradient(-90deg, rgba(255,238,185,0.25) 0%, transparent 100%)",
        }}
      />
      <div
        aria-hidden
        className="fixed inset-0 -z-10 pointer-events-none"
        style={{
          background:
            "radial-gradient(2px 3px at 14% 25%, rgba(255,245,200,0.4), transparent), radial-gradient(3px 4px at 33% 48%, rgba(255,240,190,0.3), transparent), radial-gradient(2px 3px at 55% 20%, rgba(255,242,195,0.35), transparent), radial-gradient(3px 3px at 75% 40%, rgba(255,238,185,0.25), transparent)",
        }}
      />
      <BeerBubbles />
      <BeerFoamCollar />
      {/* Ruimte onder schuimkraag zodat titel/taalwisselaar niet overlappen met schuim */}
      <div
        className="relative z-10"
        style={{
          paddingTop: `max(5rem, ${Math.round(BEER_FOAM_COLLAR_HEIGHT_PX * 0.72)}px)`,
        }}
      >
        {children}
      </div>
    </div>
  )
}
