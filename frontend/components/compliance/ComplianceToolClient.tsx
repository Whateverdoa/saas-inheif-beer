"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import type { Locale } from "@/lib/i18n/config"
import { withLocale } from "@/lib/i18n/config"
import { beerApi, type ComplianceTextResponse, type EULanguage } from "@/lib/api/beer"
import type { ComplianceToolMessages } from "@/lib/i18n/types"

import { COMMON_ALLERGENS, COMMON_INGREDIENTS } from "./compliance-constants"

export function ComplianceToolClient({
  t,
  locale,
}: {
  t: ComplianceToolMessages
  locale: Locale
}) {
  const [languages, setLanguages] = useState<EULanguage[]>([])
  const [selectedLanguages, setSelectedLanguages] = useState(["en", "nl", "de", "fr"])
  const [abv, setAbv] = useState(5.0)
  const [ingredients, setIngredients] = useState(["water", "barley malt", "hops", "yeast"])
  const [allergens, setAllergens] = useState(["gluten", "barley"])
  const [producer, setProducer] = useState("Your Brewery Name")
  const [country, setCountry] = useState("Netherlands")
  const [complianceText, setComplianceText] = useState<ComplianceTextResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    let c = false
    ;(async () => {
      try {
        const langs = await beerApi.getLanguages()
        if (!c) setLanguages(langs)
      } catch (e) {
        console.error(e)
      } finally {
        if (!c) setLoading(false)
      }
    })()
    return () => {
      c = true
    }
  }, [])

  const toggleLanguage = (code: string) => {
    setSelectedLanguages((prev) =>
      prev.includes(code) ? prev.filter((l) => l !== code) : [...prev, code],
    )
  }
  const toggleIngredient = (ing: string) => {
    setIngredients((prev) => (prev.includes(ing) ? prev.filter((i) => i !== ing) : [...prev, ing]))
  }
  const toggleAllergen = (all: string) => {
    setAllergens((prev) => (prev.includes(all) ? prev.filter((a) => a !== all) : [...prev, all]))
  }

  const generateText = async () => {
    if (selectedLanguages.length === 0) return
    setGenerating(true)
    try {
      const result = await beerApi.generateComplianceText({
        languages: selectedLanguages,
        abv,
        ingredients,
        allergens,
        producer,
        country,
      })
      setComplianceText(result)
    } catch (err) {
      console.error(err)
    } finally {
      setGenerating(false)
    }
  }

  const beerHref = withLocale(locale, "/beer")

  if (loading) {
    return (
      <div className="min-h-screen bg-amber-50/30 dark:bg-zinc-950 flex items-center justify-center">
        <div className="text-lg text-zinc-600 dark:text-zinc-400">{t.loading}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-amber-50/30 dark:bg-zinc-950">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="mb-8 pb-6 border-b border-amber-100 dark:border-amber-900/30">
          <Link
            href={beerHref}
            className="text-amber-600 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-300 text-sm font-medium mb-3 inline-block"
          >
            {t.back}
          </Link>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-2">{t.title}</h1>
          <p className="text-zinc-600 dark:text-zinc-400">{t.subtitle}</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
              <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.targetLangs}</h2>
              <div className="flex flex-wrap gap-2">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => toggleLanguage(lang.code)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedLanguages.includes(lang.code)
                        ? "bg-amber-500 text-white"
                        : "bg-zinc-100 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-600"
                    }`}
                    title={lang.english_name}
                  >
                    {lang.native_name}
                  </button>
                ))}
              </div>
              <p className="text-xs text-zinc-500 mt-3">
                {t.selected} {selectedLanguages.length} / 24
              </p>
            </div>

            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
              <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.beerDetails}</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                    {t.abv}
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min={0}
                    max={100}
                    value={abv}
                    onChange={(e) => setAbv(parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                    {t.producer}
                  </label>
                  <input
                    type="text"
                    value={producer}
                    onChange={(e) => setProducer(e.target.value)}
                    className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                    {t.country}
                  </label>
                  <input
                    type="text"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white"
                  />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
              <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.ingredients}</h2>
              <div className="flex flex-wrap gap-2">
                {COMMON_INGREDIENTS.map((ing) => (
                  <button
                    key={ing}
                    type="button"
                    onClick={() => toggleIngredient(ing)}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                      ingredients.includes(ing)
                        ? "bg-green-500 text-white"
                        : "bg-zinc-100 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200"
                    }`}
                  >
                    {ing}
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
              <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.allergens}</h2>
              <div className="flex flex-wrap gap-2">
                {COMMON_ALLERGENS.map((all) => (
                  <button
                    key={all}
                    type="button"
                    onClick={() => toggleAllergen(all)}
                    className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                      allergens.includes(all)
                        ? "bg-red-500 text-white"
                        : "bg-zinc-100 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200"
                    }`}
                  >
                    {all}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="button"
              onClick={() => void generateText()}
              disabled={generating || selectedLanguages.length === 0}
              className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                generating || selectedLanguages.length === 0
                  ? "bg-zinc-300 dark:bg-zinc-700 text-zinc-500 cursor-not-allowed"
                  : "bg-amber-500 hover:bg-amber-600 text-white"
              }`}
            >
              {generating ? t.generating : t.generate}
            </button>
          </div>

          <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-white">{t.output}</h2>
            {!complianceText ? (
              <div className="text-center text-zinc-400 dark:text-zinc-500 py-12">
                <p>{t.empty}</p>
              </div>
            ) : (
              <div className="space-y-6 max-h-[70vh] overflow-y-auto">
                {Object.entries(complianceText).map(([langCode, text]) => {
                  const langInfo = languages.find((l) => l.code === langCode)
                  const fullText = `${text.ingredients_label}: ${text.ingredients_text}\n${text.contains_label}: ${text.allergens_text}\n${text.abv_label}: ${text.abv_text}\n${text.producer_label}: ${text.producer_text}\n${text.country_label}: ${text.country_text}\n\n${text.warning_text}\n${text.age_warning}`
                  return (
                    <div
                      key={langCode}
                      className="border-b border-zinc-200 dark:border-zinc-700 pb-4 last:border-0"
                    >
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-lg font-semibold text-zinc-900 dark:text-white">
                          {langInfo?.native_name || langCode.toUpperCase()}
                        </span>
                        <span className="text-xs text-zinc-500 uppercase">({langCode})</span>
                      </div>
                      <div className="bg-zinc-50 dark:bg-zinc-900 rounded-lg p-4 text-sm font-mono space-y-2">
                        <p>
                          <strong>{text.ingredients_label}:</strong> {text.ingredients_text}
                        </p>
                        <p>
                          <strong>{text.contains_label}:</strong>{" "}
                          <span className="text-red-600 dark:text-red-400 font-bold">
                            {text.allergens_text}
                          </span>
                        </p>
                        <p>
                          <strong>{text.abv_label}:</strong> {text.abv_text}
                        </p>
                        <p>
                          <strong>{text.producer_label}:</strong> {text.producer_text}
                        </p>
                        <p>
                          <strong>{text.country_label}:</strong> {text.country_text}
                        </p>
                        <hr className="border-zinc-300 dark:border-zinc-700 my-2" />
                        <p className="text-amber-600 dark:text-amber-400">⚠️ {text.warning_text}</p>
                        <p className="text-red-600 dark:text-red-400">🔞 {text.age_warning}</p>
                      </div>
                      <button
                        type="button"
                        onClick={() => void navigator.clipboard.writeText(fullText)}
                        className="mt-2 text-xs text-amber-600 hover:text-amber-700"
                      >
                        {t.copy}
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
