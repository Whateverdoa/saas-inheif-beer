import Link from "next/link"

import type { Locale } from "@/lib/i18n/config"
import { withLocale } from "@/lib/i18n/config"
import type { HomeMessages } from "@/lib/i18n/types"

const btnPrimary =
  "inline-flex items-center justify-center px-8 py-3.5 rounded-[60px] font-bold text-sm bg-[#4a2800] text-[#fffef5] shadow-lg hover:translate-y-[-2px] transition"
const btnGhost =
  "inline-flex items-center justify-center px-8 py-3.5 rounded-[60px] font-bold text-sm border-2 border-[#4a2800]/25 text-[#4a2800] hover:border-[#4a2800]/45 transition bg-white/20"

export function BrewTagHome({
  home,
  locale,
}: {
  home: HomeMessages
  locale: Locale
}) {
  const orderHref = withLocale(locale, "/beer/order")
  const complianceHref = withLocale(locale, "/beer/compliance")

  return (
    <div className="relative z-10 max-w-[640px] mx-auto px-6 pb-16">
      <section className="pt-4 md:pt-8 pb-12 text-center">
        <p className="inline-block text-xs font-semibold uppercase tracking-[0.12em] text-[#6b3e06] border border-[#3a2501]/15 bg-[#3a2501]/10 px-5 py-1.5 rounded-full mb-6">
          {home.badge}
        </p>
        <h1 className="font-brew-heading font-black text-[clamp(2.25rem,7vw,3.75rem)] leading-[0.95] text-[#4a2800] drop-shadow-[0_2px_20px_rgba(245,212,66,0.35)]">
          {home.titleLine1}
          <span className="block text-[0.42em] font-brew-sans font-medium tracking-[0.08em] uppercase text-[#6b3e06] mt-3">
            {home.titleLine2}
          </span>
        </h1>
        <p className="mt-6 text-base md:text-lg text-[#6b3e06] max-w-lg mx-auto leading-relaxed">
          {home.intro}
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center mt-10">
          <Link href={orderHref} className={btnPrimary}>
            {home.ctaPrimary}
          </Link>
          <Link href={complianceHref} className={btnGhost}>
            {home.ctaSecondary}
          </Link>
        </div>
      </section>

      <footer className="mt-8 text-center text-sm text-[#4a2800]/70">
        © {new Date().getFullYear()} {home.footer}
      </footer>
    </div>
  )
}
