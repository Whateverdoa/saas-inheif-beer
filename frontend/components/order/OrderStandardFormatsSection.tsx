"use client"

import type { BeerLabelType } from "@/lib/api/beer"
import type { OrderMessages } from "@/lib/i18n/types"

type FormatCopy = Pick<
  OrderMessages,
  | "standardFormatsTitle"
  | "standardFormatsHint"
  | "loadingFormats"
  | "formatsError"
  | "clearStandard"
>

const h2 = "font-brew-heading font-bold text-xl border-b border-[#4a2800]/10 pb-3 mb-3"
const chipBase =
  "rounded-xl border-2 px-3 py-2 text-left text-sm transition bg-white/25 border-[#4a2800]/8 hover:border-[#4a2800]/20"
const chipOn = "border-[#b8860b] bg-[#b8860b]/15"

export function OrderStandardFormatsSection({
  t,
  formats,
  loading,
  fetchFailed,
  selectedId,
  onSelect,
  onClear,
}: {
  t: FormatCopy
  formats: BeerLabelType[]
  loading: boolean
  fetchFailed: boolean
  selectedId: string | null
  onSelect: (lt: BeerLabelType) => void
  onClear: () => void
}) {
  return (
    <section className="mb-8" aria-label={t.standardFormatsTitle}>
      <h2 className={h2}>{t.standardFormatsTitle}</h2>
      <p className="text-sm text-[#6b3e06] mb-4 leading-relaxed">{t.standardFormatsHint}</p>
      {loading ? <p className="text-sm text-[#6b3e06]">{t.loadingFormats}</p> : null}
      {fetchFailed ? <p className="text-sm text-red-800">{t.formatsError}</p> : null}
      {!loading && !fetchFailed && formats.length > 0 ? (
        <div className="flex flex-wrap gap-2 mb-3">
          {formats.map((lt) => (
            <button
              key={lt.id}
              type="button"
              onClick={() => onSelect(lt)}
              className={`${chipBase} ${selectedId === lt.id ? chipOn : ""}`}
            >
              <span className="font-semibold text-[#4a2800] block">{lt.name}</span>
              <span className="text-xs text-[#6b3e06]">
                {lt.width_mm} × {lt.height_mm} mm
                {lt.category ? ` · ${lt.category}` : ""}
              </span>
            </button>
          ))}
        </div>
      ) : null}
      {!loading && !fetchFailed && selectedId ? (
        <button
          type="button"
          onClick={onClear}
          className="text-sm font-medium text-[#6b3e06] underline decoration-[#4a2800]/30 hover:text-[#4a2800]"
        >
          {t.clearStandard}
        </button>
      ) : null}
    </section>
  )
}
