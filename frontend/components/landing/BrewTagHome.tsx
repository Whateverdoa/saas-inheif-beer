import Link from "next/link"

const btnPrimary =
  "inline-flex items-center justify-center px-8 py-3.5 rounded-[60px] font-bold text-sm bg-[#4a2800] text-[#fffef5] shadow-lg hover:translate-y-[-2px] transition"
const btnGhost =
  "inline-flex items-center justify-center px-8 py-3.5 rounded-[60px] font-bold text-sm border-2 border-[#4a2800]/25 text-[#4a2800] hover:border-[#4a2800]/45 transition bg-white/20"

const glassCard =
  "rounded-[20px] border border-white/30 bg-white/20 backdrop-blur-md p-9 shadow-sm"

export function BrewTagHome() {
  return (
    <div className="relative z-10 max-w-[900px] mx-auto px-6 pb-16">
      <section className="pt-28 md:pt-40 pb-20 text-center">
        <p className="inline-block text-xs font-semibold uppercase tracking-[0.12em] text-[#6b3e06] border border-[#3a2501]/15 bg-[#3a2501]/10 px-5 py-1.5 rounded-full mb-7">
          Custom beer labels — craft your identity
        </p>
        <h1 className="font-brew-heading font-black text-[clamp(2.5rem,8vw,4.5rem)] leading-[0.95] text-[#4a2800] drop-shadow-[0_2px_20px_rgba(245,212,66,0.4)]">
          INHEIF
          <span className="block text-[0.42em] font-brew-sans font-medium tracking-[0.08em] uppercase text-[#6b3e06] mt-3">
            Labels as unique as your brew
          </span>
        </h1>
        <p className="mt-6 text-lg text-[#6b3e06] max-w-xl mx-auto leading-relaxed">
          Professional labels for craft breweries and beer brands. Dutch formats for bottles
          and cans — print-ready, waterproof options, OGOS-backed production.
        </p>
        <div className="flex flex-wrap gap-4 justify-center mt-10">
          <Link href="/beer/order" className={btnPrimary}>
            Start your order →
          </Link>
          <Link href="#showcase" className={btnGhost}>
            See examples
          </Link>
        </div>
      </section>

      <section className="mb-20">
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: "🎨",
              title: "Design-ready",
              text: "Upload artwork or work from standard beer label dimensions. Full bleed and CMYK.",
            },
            {
              icon: "🏷️",
              title: "Premium materials",
              text: "Vinyl, paper, kraft — built to survive the cold chain and the ice bucket.",
            },
            {
              icon: "📦",
              title: "Flexible volumes",
              text: "From small runs to production scale. Transparent pricing tiers.",
            },
          ].map((f) => (
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
          Made for every style
        </h2>
        <p className="text-[#6b3e06] mb-10 max-w-lg mx-auto">
          From hazy IPAs to imperial stouts — your label tells your story before the first sip.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          {[
            { name: "Midnight", type: "Imperial Stout", abv: "11.5% ABV" },
            { name: "Copperline", type: "Amber Ale", abv: "5.8% ABV" },
            { name: "Forest Floor", type: "Farmhouse Saison", abv: "6.2% ABV" },
            { name: "Ember", type: "Barrel-Aged Red", abv: "9.0% ABV" },
          ].map((l) => (
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
          How it works
        </h2>
        <div className="grid sm:grid-cols-2 gap-8">
          {[
            ["1", "Configure", "Pick format, material, and quantity in our beer label flow."],
            ["2", "Upload", "Send your PDF or design notes — we validate print specs."],
            ["3", "Proof", "Digital proof for approval or revisions."],
            ["4", "Print & ship", "Production and delivery to your brewery or warehouse."],
          ].map(([n, t, d]) => (
            <div key={n} className="text-center">
              <div className="w-12 h-12 rounded-full bg-[#4a2800] text-[#f0c632] font-brew-heading font-bold text-xl flex items-center justify-center mx-auto mb-4">
                {n}
              </div>
              <h4 className="font-semibold text-[#4a2800] mb-2">{t}</h4>
              <p className="text-sm text-[#6b3e06]">{d}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="pricing" className="mb-20 scroll-mt-24">
        <h2 className="font-brew-heading font-bold text-3xl text-center text-[#4a2800] mb-3">
          Simple pricing
        </h2>
        <p className="text-center text-[#6b3e06] mb-10">
          Transparent quotes — request a tailored offer for your volume.
        </p>
        <div className="grid md:grid-cols-3 gap-5 max-w-4xl mx-auto">
          {[
            { tier: "Starter", price: "€0,38", unit: "per label · 50–500", feat: ["Waterproof vinyl", "Full colour", "5-day turnaround"] },
            { tier: "Craft Pro", price: "€0,18", unit: "per label · 500–10K", feat: ["Premium stocks", "Foil options", "3-day turnaround"], featured: true },
            { tier: "Production", price: "€0,06", unit: "per label · 10K+", feat: ["All finishes", "Priority production", "Volume agreements"] },
          ].map((p) => (
            <div
              key={p.tier}
              className={`rounded-[20px] p-8 text-center border ${
                p.featured
                  ? "bg-[#78350f]/85 text-[#fffef5] border-amber-200/30 scale-[1.02] shadow-xl"
                  : "bg-white/25 border-white/35"
              }`}
            >
              <div className="text-sm font-semibold opacity-90">{p.tier}</div>
              <div className="font-brew-heading font-black text-4xl mt-2">{p.price}</div>
              <div className={`text-xs mt-1 ${p.featured ? "text-amber-100/90" : "text-[#6b3e06]"}`}>
                {p.unit}
              </div>
              <ul className="text-left text-sm mt-6 space-y-2 mb-8">
                {p.feat.map((x) => (
                  <li key={x}>✓ {x}</li>
                ))}
              </ul>
              <Link
                href="/beer/order"
                className={
                  p.featured
                    ? "block w-full py-3 rounded-[60px] font-bold bg-[#f0c632] text-[#4a2800] text-center"
                    : "block w-full py-3 rounded-[60px] font-bold border-2 border-[#4a2800] text-[#4a2800] text-center bg-white/15 hover:bg-white/25"
                }
              >
                Get quote
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-[28px] border border-white/35 bg-white/20 backdrop-blur-lg px-8 py-14 text-center">
        <h2 className="font-brew-heading font-bold text-2xl md:text-3xl text-[#4a2800] mb-4">
          Ready to label your brew?
        </h2>
        <p className="text-[#6b3e06] mb-8 max-w-md mx-auto">
          Get a custom quote in under 2 minutes. No commitment.
        </p>
        <Link href="/beer/order" className={btnPrimary}>
          Start your order →
        </Link>
      </section>

      <footer className="mt-14 text-center text-sm text-[#4a2800]/70">
        © {new Date().getFullYear()} INHEIF · Beer labels · Powered by OGOS
      </footer>
    </div>
  )
}
