"use client"

import { useCallback, useState } from "react"
import Link from "next/link"
import { KvkLookup } from "@/components/kvk/KvkLookup"
import type { KvkCompany } from "@/lib/api/kvk"

const input =
  "w-full px-4 py-3 rounded-xl border-[1.5px] border-[#4a2800]/10 bg-white/45 focus:border-[#b8860b] focus:bg-white/65 outline-none text-[#4a2800]"
const labelCls = "block text-[0.8rem] font-semibold text-[#6b3e06] mb-1 tracking-wide"

export function BeerOrderForm() {
  const [contactName, setContactName] = useState("")
  const [companyName, setCompanyName] = useState("")
  const [email, setEmail] = useState("")
  const [phone, setPhone] = useState("")
  const [addrStreet, setAddrStreet] = useState("")
  const [addrCity, setAddrCity] = useState("")
  const [labelShape, setLabelShape] = useState("rechthoek")
  const [dimensions, setDimensions] = useState("")
  const [material, setMaterial] = useState("vinyl")
  const [quantity, setQuantity] = useState(500)
  const [notes, setNotes] = useState("")
  const [addrFromKvk, setAddrFromKvk] = useState(false)

  const applyKvk = useCallback((c: KvkCompany) => {
    setCompanyName(c.name)
    const streetLine = [c.street, c.house_number, c.house_number_addition]
      .filter(Boolean)
      .join(" ")
    setAddrStreet(streetLine)
    setAddrCity([c.postal_code, c.city].filter(Boolean).join(" ").trim())
    setAddrFromKvk(true)
  }, [])

  const clearKvk = useCallback(() => {
    setAddrFromKvk(false)
  }, [])

  const submit = () => {
    // TODO: POST to backend quote endpoint
    console.info("Quote request", {
      contactName,
      companyName,
      email,
      phone,
      addrStreet,
      addrCity,
      labelShape,
      dimensions,
      material,
      quantity,
      notes,
    })
    alert(
      "Bedankt! Offerte-aanvraag voorbereid (nog geen e-mailkoppeling). " +
        "Controleer de console voor de payload.",
    )
  }

  const mats = [
    { id: "vinyl", icon: "💧", name: "Vinyl", desc: "Waterbestendig" },
    { id: "papier", icon: "📄", name: "Papier", desc: "Gesatineerd" },
    { id: "kraft", icon: "🌾", name: "Kraft", desc: "Ambachtelijk" },
    { id: "textuur", icon: "🏔️", name: "Textuur", desc: "Premium" },
  ]

  const shapes = [
    { id: "rond", icon: "⬤", name: "Rond" },
    { id: "rechthoek", icon: "▬", name: "Rechthoek" },
    { id: "ovaal", icon: "⬮", name: "Ovaal" },
    { id: "custom", icon: "✦", name: "Op maat" },
  ]

  return (
    <div className="relative z-10 max-w-[720px] mx-auto px-6 pb-16 font-brew-sans">
      <header className="pt-24 md:pt-32 pb-10 text-center text-[#4a2800]">
        <Link href="/" className="text-sm font-medium text-[#6b3e06] hover:text-[#4a2800] mb-4 inline-block">
          ← Home
        </Link>
        <h1 className="font-brew-heading font-black text-[clamp(2rem,6vw,3.2rem)] leading-none mb-3">
          Bestel je labels
        </h1>
        <p className="text-[#6b3e06] max-w-md mx-auto">
          Vul het formulier in voor een vrijblijvende offerte — binnen 24 uur reactie.
        </p>
      </header>

      <div className="rounded-3xl border border-white/30 bg-white/15 backdrop-blur-md p-8 md:p-11 mb-10">
        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-6">
          Jouw gegevens
        </h2>
        <KvkLookup onFound={applyKvk} onClear={clearKvk} />

        <div className="grid sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className={labelCls}>Contactpersoon</label>
            <input className={input} value={contactName} onChange={(e) => setContactName(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>Bedrijf / brouwerij</label>
            <input
              className={input}
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Wordt ingevuld via KVK"
            />
          </div>
          <div>
            <label className={labelCls}>E-mail</label>
            <input type="email" className={input} value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>Telefoon</label>
            <input type="tel" className={input} value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
        </div>

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          Type label
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
          {shapes.map((s) => (
            <label key={s.id} className="cursor-pointer">
              <input
                type="radio"
                name="shape"
                className="peer sr-only"
                checked={labelShape === s.id}
                onChange={() => setLabelShape(s.id)}
              />
              <div className="peer-checked:border-[#b8860b] peer-checked:bg-[#b8860b]/15 flex flex-col items-center p-3 rounded-xl border-2 border-[#4a2800]/8 bg-white/25">
                <span className="text-xl">{s.icon}</span>
                <span className="text-xs font-semibold text-[#4a2800] mt-1">{s.name}</span>
              </div>
            </label>
          ))}
        </div>
        <div>
          <label className={labelCls}>Afmeting (b × h mm)</label>
          <input
            className={input}
            value={dimensions}
            onChange={(e) => setDimensions(e.target.value)}
            placeholder="bijv. 90 × 120"
          />
        </div>

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          Materiaal
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
          {mats.map((m) => (
            <label key={m.id} className="cursor-pointer">
              <input
                type="radio"
                name="mat"
                className="peer sr-only"
                checked={material === m.id}
                onChange={() => setMaterial(m.id)}
              />
              <div className="peer-checked:border-[#b8860b] peer-checked:bg-[#b8860f]/15 flex flex-col items-center p-3 rounded-xl border-2 border-[#4a2800]/8 bg-white/25">
                <span className="text-lg">{m.icon}</span>
                <span className="text-xs font-semibold text-[#4a2800]">{m.name}</span>
                <span className="text-[0.65rem] text-[#6b3e06]">{m.desc}</span>
              </div>
            </label>
          ))}
        </div>

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          Oplage
        </h2>
        <div className="text-center mb-2">
          <span className="font-brew-heading font-black text-4xl text-[#4a2800]">{quantity}</span>
          <span className="block text-sm text-[#6b3e06]">labels</span>
        </div>
        <input
          type="range"
          min={100}
          max={10000}
          step={100}
          value={quantity}
          onChange={(e) => setQuantity(Number(e.target.value))}
          className="w-full h-2 rounded-full accent-[#b8860b]"
        />

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          Opmerkingen
        </h2>
        <textarea
          className={`${input} min-h-[90px] resize-y`}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Wensen voor folie, PMS-kleuren, leverdatum…"
        />

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          Bezorgadres
        </h2>
        {addrFromKvk && (
          <p className="text-xs text-[#6b3e06]/70 mb-2">Ingevuld via KVK — aanpasbaar.</p>
        )}
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          <div>
            <label className={labelCls}>Straat + huisnummer</label>
            <input className={input} value={addrStreet} onChange={(e) => setAddrStreet(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>Postcode + plaats</label>
            <input className={input} value={addrCity} onChange={(e) => setAddrCity(e.target.value)} />
          </div>
        </div>

        <p className="text-sm text-[#6b3e06] mb-4">
          Je ontvangt een vrijblijvende offerte op het opgegeven e-mailadres (koppeling volgt).
        </p>
        <button
          type="button"
          onClick={submit}
          className="w-full py-4 rounded-[60px] font-bold bg-[#4a2800] text-[#fffef5] hover:opacity-95"
        >
          Offerte aanvragen →
        </button>
      </div>

      <footer className="text-center text-sm text-[#4a2800]/70">
        © {new Date().getFullYear()} INHEIF · Beer labels
      </footer>
    </div>
  )
}
