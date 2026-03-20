import Link from "next/link"

import type { Locale } from "@/lib/i18n/config"
import { withLocale } from "@/lib/i18n/config"
import type { HomeMessages } from "@/lib/i18n/types"

const btnPrimary =
  "inline-flex items-center justify-center px-8 py-3.5 rounded-[60px] font-bold text-sm bg-[#4a2800] text-[#fffef5] shadow-lg hover:translate-y-[-2px] transition"
const btnGhost =
  "inline-flex items-center justify-center px-8 py-3.5 rounded-[60px] font-bold text-sm border-2 border-[#4a2800]/25 text-[#4a2800] hover:border-[#4a2800]/45 transition bg-white/20"
const glassCard =
  "rounded-[20px] border border-white/30 bg-white/20 backdrop-blur-md p-9 shadow-sm"

export function BrewTagHome({
  home,
  locale,
}: {
  home: HomeMessages
  locale: Locale
}) {
  const orderHref = withLocale(locale, "/beer/order")

  return (
    <div className="relative z-10 max-w-[900px] mx-auto px-6 pb-16">
      <section className="pt-4 md:pt-6 pb-20 text-center">
        <p className="inline-block text-xs font-semibold uppercase tracking-[0.12em] text-[#6b3e06] border border-[#3a2501]/15 bg-[#3a2501]/10 px-5 py-1.5 rounded-full mb-7">
          {home.badge}
        </p>
        <h1 className="font-brew-heading font-black text-[clamp(2.5rem,8vw,4.5rem)] leading-[0.95] text-[#4a2800] drop-shadow-[0_2px_20px_rgba(245,212,66,0.4)]">
          {home.titleLine1}
          <span className="block text-[0.42em] font-brew-sans font-medium tracking-[0.08em] uppercase text-[#6b3e06] mt-3">
            {home.titleLine2}
          </span>
        </h1>
        <p className="mt-6 text-lg text-[#6b3e06] max-w-xl mx-auto leading-relaxed">{home.intro}</p>
        <div className="flex flex-wrap gap-4 justify-center mt-10">
          <Link href={orderHref} className={btnPrimary}>
            {home.ctaOrder}
          </Link>
          <Link href="#showcase" className={btnGhost}>
            {home.ctaExamples}
          </Link>
        </div>
      </section>

      <section className="mb-20">
        <div className="grid md:grid-cols-3 gap-6">
          {home.features.map((f) => (
            <div key={f.title} className={glassCard}>
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="font-brew-heading font-bold text-xl text-[#4a2800] mb-2">{f.title}</h3>
              <p className="text-sm text-[#6b3e06] leading-relaxed">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="showcase" className="mb-20 text-center scroll-mt-24">
        <h2 className="font-brew-heading font-bold text-3xl md:text-4xl text-[#4a2800] mb-3">
          {home.showcaseTitle}
        </h2>
        <p className="text-[#6b3e06] mb-10 max-w-lg mx-auto">{home.showcaseSubtitle}</p>
        <div className="flex flex-wrap justify-center gap-4">
          {home.labels.map((l) => (
            <div
              key={l.name}
              className="w-[150px] h-[200px] md:w-[170px] md:h-[230px] rounded-2xl border-2 border-white/35 bg-gradient-to-b from-amber-100/40 to-amber-900/20 flex items-center justify-center p-3 shadow-md"
            >
              <div className="w-full h-full rounded-lg border border-white/25 flex flex-col items-center justify-center text-center p-2">
                <div className="font-brew-heading font-bold text-[#4a2800] text-sm">{l.name}</div>
                <div className="text-[0.65rem] text-[#6b3e06] mt-1">{l.type}</div>
                <div className="text-[0.7rem] font-semibold text-[#b8860b] mt-3">{l.abv}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-20">
        <h2 className="font-brew-heading font-bold text-3xl text-center text-[#4a2800] mb-10">
          {home.howTitle}
        </h2>
        <div className="grid sm:grid-cols-2 gap-8">
          {home.steps.map(({ n, title, desc }) => (
            <div key={n} className="text-center">
              <div className="w-12 h-12 rounded-full bg-[#4a2800] text-[#f0c632] font-brew-heading font-bold text-xl flex items-center justify-center mx-auto mb-4">
                {n}
              </div>
              <h4 className="font-semibold text-[#4a2800] mb-2">{title}</h4>
              <p className="text-sm text-[#6b3e06]">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="pricing" className="mb-20 scroll-mt-24">
        <h2 className="font-brew-heading font-bold text-3xl text-center text-[#4a2800] mb-3">
          {home.pricingTitle}
        </h2>
        <p className="text-center text-[#6b3e06] mb-10">{home.pricingSubtitle}</p>
        <div
          className={`grid gap-5 mx-auto ${
            home.tiers.length === 1
              ? "max-w-md"
              : "max-w-4xl md:grid-cols-3"
          }`}
        >
          {home.tiers.map((p) => (
            <div
              key={p.tier}
              className={`rounded-[20px] p-8 text-center border ${
                p.featured
                  ? "bg-[#78350f]/85 text-[#fffef5] border-amber-200/30 shadow-xl"
                  : "bg-white/25 border-white/35"
              }`}
            >
              <div className="text-sm font-semibold opacity-90">{p.tier}</div>
              <div className="font-brew-heading font-black text-4xl mt-2">{p.price}</div>
              <div
                className={`text-xs mt-1 ${
                  p.featured ? "text-amber-100/90" : "text-[#6b3e06]"
                }`}
              >
                {p.unit}
              </div>
              <ul className="text-left text-sm mt-6 space-y-2 mb-8">
                {p.feat.map((x) => (
                  <li key={x}>✓ {x}</li>
                ))}
              </ul>
              <Link
                href={orderHref}
                className={
                  p.featured
                    ? "block w-full py-3 rounded-[60px] font-bold bg-[#f0c632] text-[#4a2800] text-center"
                    : "block w-full py-3 rounded-[60px] font-bold border-2 border-[#4a2800] text-[#4a2800] text-center bg-white/15 hover:bg-white/25"
                }
              >
                {p.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-[28px] border border-white/35 bg-white/20 backdrop-blur-lg px-8 py-14 text-center">
        <h2 className="font-brew-heading font-bold text-2xl md:text-3xl text-[#4a2800] mb-4">
          {home.finalTitle}
        </h2>
        <p className="text-[#6b3e06] mb-8 max-w-md mx-auto">{home.finalSubtitle}</p>
        <Link href={orderHref} className={btnPrimary}>
          {home.ctaOrder}
        </Link>
      </section>

      <footer className="mt-14 text-center text-sm text-[#4a2800]/70">
        © {new Date().getFullYear()} {home.footer}
      </footer>
    </div>
  )
}
