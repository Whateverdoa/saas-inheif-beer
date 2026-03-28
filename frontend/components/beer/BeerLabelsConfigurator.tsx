"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import { BeerFormatsReferenceTable } from "@/components/beer/BeerFormatsReferenceTable"
import type { Locale } from "@/lib/i18n/config"
import { withLocale } from "@/lib/i18n/config"
import { beerApi, type BeerCategory, type BeerLabelType, type BeerSubstrate } from "@/lib/api/beer"
import type { BeerToolMessages } from "@/lib/i18n/types"

export function BeerLabelsConfigurator({
  t,
  locale,
}: {
  t: BeerToolMessages
  locale: Locale
}) {
  const [categories, setCategories] = useState<BeerCategory[]>([])
  const [labelTypes, setLabelTypes] = useState<BeerLabelType[]>([])
  const [substrates, setSubstrates] = useState<BeerSubstrate[]>([])
  const [selectedCategory, setSelectedCategory] = useState("")
  const [selectedLabelType, setSelectedLabelType] = useState<BeerLabelType | null>(null)
  const [selectedSubstrate, setSelectedSubstrate] = useState<BeerSubstrate | null>(null)
  const [quantity, setQuantity] = useState(1000)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        setLoading(true)
        const [cats, labels, subs] = await Promise.all([
          beerApi.getCategories(),
          beerApi.getLabelTypes(),
          beerApi.getSubstrates(),
        ])
        if (!cancelled) {
          setCategories(cats)
          setLabelTypes(labels)
          setSubstrates(subs)
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : "err"
        if (!cancelled) {
          setError(msg === "Failed to fetch" ? t.errorFetch : msg)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- server messages; fetch once on mount
  }, [])

  const filteredLabelTypes = selectedCategory
    ? labelTypes.filter((lt) => lt.category === selectedCategory)
    : labelTypes
  const recommendedSubstrates = selectedLabelType
    ? substrates.filter((s) => selectedLabelType.recommended_substrates.includes(s.name))
    : substrates
  const pageBg = "min-h-screen bg-amber-50/30 dark:bg-zinc-950"
  const home = withLocale(locale, "/")
  const order = withLocale(locale, "/beer/order")
  const compliance = withLocale(locale, "/beer/compliance")

  if (loading) {
    return (
      <div className={`${pageBg} flex items-center justify-center`}>
        <div className="text-lg text-zinc-600 dark:text-zinc-400">{t.loading}</div>
      </div>
    )
  }
  if (error) {
    return (
      <div className={`${pageBg} flex items-center justify-center px-4`}>
        <div className="text-red-500 text-lg text-center">{error}</div>
      </div>
    )
  }

  return (
    <div className={pageBg}>
      <div className="max-w-6xl mx-auto px-4 py-8">
        <header className="mb-8 pb-6 border-b border-amber-100 dark:border-amber-900/30">
          <Link
            href={home}
            className="text-amber-600 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-300 text-sm font-medium mb-3 inline-block"
          >
            {t.backHome}
          </Link>
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-1">{t.title}</h1>
              <p className="text-zinc-600 dark:text-zinc-400">{t.subtitle}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Link
                href={order}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 dark:bg-amber-500 dark:hover:bg-amber-600 text-white rounded-lg text-sm font-medium"
              >
                {t.quoteLink}
              </Link>
              <Link
                href={compliance}
                className="px-4 py-2 border border-amber-600/50 dark:border-amber-500/50 text-amber-800 dark:text-amber-300 rounded-lg text-sm font-medium hover:bg-amber-50 dark:hover:bg-amber-950/30"
              >
                {t.complianceLink}
              </Link>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80">
            <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.step1}</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                {t.category}
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value)
                  setSelectedLabelType(null)
                }}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
              >
                <option value="">{t.allCategories}</option>
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {filteredLabelTypes.map((lt) => (
                <button
                  key={lt.id}
                  type="button"
                  onClick={() => setSelectedLabelType(lt)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedLabelType?.id === lt.id
                      ? "border-amber-500 bg-amber-50 dark:bg-amber-900/20"
                      : "border-zinc-200 dark:border-zinc-600 hover:border-amber-300"
                  }`}
                >
                  <div className="font-medium text-zinc-900 dark:text-white">{lt.name}</div>
                  <div className="text-sm text-zinc-500 dark:text-zinc-400">
                    {lt.width_mm} × {lt.height_mm} mm
                  </div>
                  {lt.description && (
                    <div className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">{lt.description}</div>
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80">
            <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.step2}</h2>
            {selectedLabelType && (
              <div className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-sm">
                <span className="font-medium">
                  {t.recommended} {selectedLabelType.name}:
                </span>
                <div className="text-amber-700 dark:text-amber-300">
                  {selectedLabelType.recommended_substrates.join(", ")}
                </div>
              </div>
            )}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {(selectedLabelType ? recommendedSubstrates : substrates).map((sub) => (
                <button
                  key={sub.code}
                  type="button"
                  onClick={() => setSelectedSubstrate(sub)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedSubstrate?.code === sub.code
                      ? "border-amber-500 bg-amber-50 dark:bg-amber-900/20"
                      : "border-zinc-200 dark:border-zinc-600 hover:border-amber-300"
                  }`}
                >
                  <div className="font-medium text-zinc-900 dark:text-white">{sub.name}</div>
                  <div className="flex gap-2 mt-1">
                    {sub.is_waterproof && (
                      <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded">
                        {t.waterproof}
                      </span>
                    )}
                    {sub.is_biodegradable && (
                      <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded">
                        {t.eco}
                      </span>
                    )}
                    <span className="text-xs px-2 py-0.5 bg-zinc-100 dark:bg-zinc-700 text-zinc-600 dark:text-zinc-300 rounded capitalize">
                      {sub.finish}
                    </span>
                  </div>
                  {sub.description && (
                    <div className="text-xs text-zinc-400 dark:text-zinc-500 mt-2">{sub.description}</div>
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm border border-zinc-200/80 dark:border-zinc-700/80">
            <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.step3}</h2>
            <div className="mb-6">
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                {t.qty}
              </label>
              <input
                type="number"
                min={100}
                step={100}
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value, 10) || 100)}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
              />
            </div>
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">{t.summaryFormat}</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {selectedLabelType?.name || "—"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">{t.summaryDimensions}</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {selectedLabelType ? `${selectedLabelType.width_mm} × ${selectedLabelType.height_mm} mm` : "—"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">{t.summarySubstrate}</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {selectedSubstrate?.name || "—"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-zinc-500 dark:text-zinc-400">{t.summaryQty}</span>
                <span className="font-medium text-zinc-900 dark:text-white">
                  {quantity.toLocaleString()} {t.summaryQtyUnit}
                </span>
              </div>
            </div>
            <hr className="my-4 border-zinc-200 dark:border-zinc-700" />
            <div className="mb-6">
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                {t.uploadTitle}
              </label>
              <div className="border-2 border-dashed border-zinc-300 dark:border-zinc-600 rounded-lg p-6 text-center">
                <div className="text-zinc-400 dark:text-zinc-500 text-sm">{t.uploadHint}</div>
                <p className="text-xs mt-1 text-zinc-400">{t.uploadSub}</p>
                <input
                  type="file"
                  accept=".pdf"
                  className="hidden"
                  style={{ display: "none" }}
                  tabIndex={-1}
                  aria-hidden
                />
              </div>
            </div>
            <button
              type="button"
              disabled={!selectedLabelType || !selectedSubstrate}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                selectedLabelType && selectedSubstrate
                  ? "bg-amber-600 hover:bg-amber-700 dark:bg-amber-500 dark:hover:bg-amber-600 text-white"
                  : "bg-zinc-200 dark:bg-zinc-700 text-zinc-400 cursor-not-allowed"
              }`}
            >
              {t.checkout}
            </button>
            {(!selectedLabelType || !selectedSubstrate) && (
              <p className="text-xs text-zinc-400 dark:text-zinc-500 text-center mt-2">{t.selectBoth}</p>
            )}
          </div>
        </div>

        <BeerFormatsReferenceTable labelTypes={labelTypes} t={t} />
      </div>
    </div>
  )
}
