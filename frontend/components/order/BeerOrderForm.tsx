"use client"

import Link from "next/link"
import { useCallback, useEffect, useMemo, useState } from "react"

import { KvkLookup } from "@/components/kvk/KvkLookup"
import { LabelPdfInsight } from "@/components/order/LabelPdfInsight"
import { LabelSetUpload, type LabelFileMap } from "@/components/order/LabelSetUpload"
import { OrderQuantitySection } from "@/components/order/OrderQuantitySection"
import { OrderStandardFormatsSection } from "@/components/order/OrderStandardFormatsSection"
import { useBeerLabelTypes } from "@/components/order/use-beer-label-types"
import { beerApi, type BeerLabelType, type PDFValidationResult } from "@/lib/api/beer"
import type { Locale } from "@/lib/i18n/config"
import { withLocale } from "@/lib/i18n/config"
import type { KvkCompany } from "@/lib/api/kvk"
import type { KvkMessages, OrderMessages } from "@/lib/i18n/types"

const inputCls =
  "w-full px-4 py-3 rounded-xl border-[1.5px] border-[#4a2800]/10 bg-white/45 focus:border-[#b8860b] focus:bg-white/65 outline-none text-[#4a2800]"
const labelCls = "block text-[0.8rem] font-semibold text-[#6b3e06] mb-1 tracking-wide"

const SHAPE_IDS = new Set(["rond", "rechthoek", "ovaal", "custom"])

export function BeerOrderForm({
  messages: t,
  kvk,
  locale,
}: {
  messages: OrderMessages
  kvk: KvkMessages
  locale: Locale
}) {
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
  const [standardPresetId, setStandardPresetId] = useState<string | null>(null)
  const [labelFiles, setLabelFiles] = useState<LabelFileMap>({})
  const [frontInsight, setFrontInsight] = useState<PDFValidationResult | null>(null)
  const [insightLoading, setInsightLoading] = useState(false)
  const [insightError, setInsightError] = useState<string | null>(null)

  const { formats, loading: formatsLoading, error: formatsErr } = useBeerLabelTypes()
  const formatsFetchFailed = formatsErr !== null

  const homeHref = withLocale(locale, "/")

  const suggestedShapeLabel = useMemo(() => {
    const id = frontInsight?.suggested_shape
    if (!id) return null
    return t.shapes.find((s) => s.id === id)?.name ?? null
  }, [frontInsight?.suggested_shape, t.shapes])

  useEffect(() => {
    const file = labelFiles.front
    if (!file) {
      setFrontInsight(null)
      setInsightError(null)
      setInsightLoading(false)
      return
    }

    const ac = new AbortController()
    setInsightLoading(true)
    setInsightError(null)

    beerApi
      .preflightLabelPdf(file, { signal: ac.signal })
      .then((r) => {
        setFrontInsight(r)
        if (r.dimensions_display) {
          setDimensions(r.dimensions_display)
        }
        if (r.suggested_shape && SHAPE_IDS.has(r.suggested_shape)) {
          setLabelShape(r.suggested_shape)
        }
        if (r.matched_standard_label_type_id) {
          setStandardPresetId(r.matched_standard_label_type_id)
        }
        setInsightLoading(false)
      })
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return
        setFrontInsight(null)
        setInsightError(e instanceof Error ? e.message : String(e))
        setInsightLoading(false)
      })

    return () => ac.abort()
  }, [labelFiles.front])

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

  const applyStandardFormat = useCallback((lt: BeerLabelType) => {
    setStandardPresetId(lt.id)
    setDimensions(`${lt.width_mm} × ${lt.height_mm}`)
    setLabelShape("rechthoek")
  }, [])

  const clearStandardFormat = useCallback(() => {
    setStandardPresetId(null)
    setDimensions("")
  }, [])

  const submit = () => {
    if (!labelFiles.front) {
      alert(t.uploadFrontRequired)
      return
    }
    const labelPayload = (Object.entries(labelFiles) as [keyof LabelFileMap, File][]).map(
      ([role, file]) => ({
        role,
        name: file.name,
        size: file.size,
      })
    )
    const quotePayload = {
      draft: true,
      note: t.alert,
      labelFiles: labelPayload,
      contactName,
      companyName,
      email,
      phone,
      shipping: { street: addrStreet, city: addrCity },
      label: {
        shape: labelShape,
        dimensionsMm: dimensions,
        material,
        quantity,
        notes,
        standardLabelTypeId: standardPresetId,
      },
      preflightFront: frontInsight,
    }
    console.info("Quote request", quotePayload)
    alert(JSON.stringify(quotePayload, null, 2))
  }

  const mats = t.mats
  const shapes = t.shapes

  return (
    <div className="relative z-10 max-w-[720px] mx-auto px-6 pb-16 font-brew-sans">
      <header className="pt-2 md:pt-4 pb-10 text-center text-[#4a2800]">
        <Link href={homeHref} className="text-sm font-medium text-[#6b3e06] hover:text-[#4a2800] mb-4 inline-block">
          {t.backHome}
        </Link>
        <h1 className="font-brew-heading font-black text-[clamp(2rem,6vw,3.2rem)] leading-none mb-3">
          {t.title}
        </h1>
        <p className="text-[#6b3e06] max-w-md mx-auto">{t.subtitle}</p>
        <p className="mt-4 text-[#4a2800] font-brew-heading font-bold text-lg max-w-lg mx-auto">
          {t.promoLine}
        </p>
      </header>

      <div className="rounded-3xl border border-white/30 bg-white/15 backdrop-blur-md p-8 md:p-11 mb-10">
        <LabelSetUpload t={t} files={labelFiles} onChange={setLabelFiles} />
        <LabelPdfInsight
          t={t}
          loading={insightLoading}
          errorMessage={insightError}
          result={frontInsight}
          shapeLabel={suggestedShapeLabel}
        />
        <OrderStandardFormatsSection
          t={t}
          formats={formats}
          loading={formatsLoading}
          fetchFailed={formatsFetchFailed}
          selectedId={standardPresetId}
          onSelect={applyStandardFormat}
          onClear={clearStandardFormat}
        />
        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-6">
          {t.yourDetails}
        </h2>
        <KvkLookup messages={kvk} onFound={applyKvk} onClear={clearKvk} />

        <div className="grid sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className={labelCls}>{t.contact}</label>
            <input className={inputCls} value={contactName} onChange={(e) => setContactName(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>{t.company}</label>
            <input
              className={inputCls}
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder={t.companyPh}
            />
          </div>
          <div>
            <label className={labelCls}>{t.email}</label>
            <input type="email" className={inputCls} value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>{t.phone}</label>
            <input type="tel" className={inputCls} value={phone} onChange={(e) => setPhone(e.target.value)} />
          </div>
        </div>

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          {t.labelType}
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
          <label className={labelCls}>{t.dimLabel}</label>
          <input
            className={inputCls}
            value={dimensions}
            onChange={(e) => setDimensions(e.target.value)}
            placeholder={t.dimPh}
          />
        </div>

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          {t.material}
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
          {mats.map((mat) => (
            <label key={mat.id} className="cursor-pointer">
              <input
                type="radio"
                name="mat"
                className="peer sr-only"
                checked={material === mat.id}
                onChange={() => setMaterial(mat.id)}
              />
              <div className="peer-checked:border-[#b8860b] peer-checked:bg-[#b8860f]/15 flex flex-col items-center p-3 rounded-xl border-2 border-[#4a2800]/8 bg-white/25">
                <span className="text-lg">{mat.icon}</span>
                <span className="text-xs font-semibold text-[#4a2800]">{mat.name}</span>
                <span className="text-[0.65rem] text-[#6b3e06]">{mat.desc}</span>
              </div>
            </label>
          ))}
        </div>

        <OrderQuantitySection
          t={t}
          locale={locale}
          quantity={quantity}
          onQuantityChange={setQuantity}
        />

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          {t.notes}
        </h2>
        <textarea
          className={`${inputCls} min-h-[90px] resize-y`}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder={t.notesPh}
        />

        <h2 className="font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-4 mt-8">
          {t.shipTitle}
        </h2>
        {addrFromKvk && <p className="text-xs text-[#6b3e06]/70 mb-2">{t.kvkFilled}</p>}
        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          <div>
            <label className={labelCls}>{t.street}</label>
            <input className={inputCls} value={addrStreet} onChange={(e) => setAddrStreet(e.target.value)} />
          </div>
          <div>
            <label className={labelCls}>{t.city}</label>
            <input className={inputCls} value={addrCity} onChange={(e) => setAddrCity(e.target.value)} />
          </div>
        </div>

        <p className="text-sm text-[#6b3e06] mb-4">{t.disclaimer}</p>
        <button
          type="button"
          onClick={submit}
          className="w-full py-4 rounded-[60px] font-bold bg-[#4a2800] text-[#fffef5] hover:opacity-95"
        >
          {t.submit}
        </button>
      </div>

      <footer className="text-center text-sm text-[#4a2800]/70">
        © {new Date().getFullYear()} {t.footer}
      </footer>
    </div>
  )
}
